// Package i18n provides the frontend i18n runtime and dictionary management
// for NAS Doctor. Dictionaries are embedded as JSON files under locales/.
//
// To add a new language: drop a new <code>.json file in locales/ and rebuild.
// No Go or HTML changes are required.
package i18n

import (
	"embed"
	"encoding/json"
	"fmt"
	"net/http"
	"sort"
	"strings"
)

//go:embed locales/*.json
var localesFS embed.FS

// DefaultLang is the fallback language and must always have a complete
// dictionary. It is served alongside any user-selected language so the
// runtime can fall back to it for missing keys.
const DefaultLang = "en"

// Supported returns the sorted list of available language codes, derived
// from the JSON files present in locales/ at compile time. Adding a new
// language is therefore purely additive: drop a file and rebuild.
func Supported() []string {
	entries, err := localesFS.ReadDir("locales")
	if err != nil {
		return []string{DefaultLang}
	}
	var out []string
	for _, e := range entries {
		if !e.IsDir() && strings.HasSuffix(e.Name(), ".json") {
			out = append(out, strings.TrimSuffix(e.Name(), ".json"))
		}
	}
	sort.Strings(out)
	if len(out) == 0 {
		return []string{DefaultLang}
	}
	return out
}

// IsValid reports whether lang is a registered language code.
func IsValid(lang string) bool {
	if lang == "" {
		return false
	}
	for _, code := range Supported() {
		if code == lang {
			return true
		}
	}
	return false
}

// loadDictionary reads and parses a single locale JSON file.
func loadDictionary(lang string) (map[string]string, error) {
	data, err := localesFS.ReadFile("locales/" + lang + ".json")
	if err != nil {
		return nil, err
	}
	var dict map[string]string
	if err := json.Unmarshal(data, &dict); err != nil {
		return nil, err
	}
	return dict, nil
}

// ResolveLanguage determines the user's preferred language from, in order:
//  1. ?lang= query parameter
//  2. nas-doctor-lang cookie (written by the frontend on language switch)
//  3. Accept-Language header (first prefix match against supported)
//  4. DefaultLang
//
// This runs server-side so the very first /js/i18n.js response already
// contains the right dictionary, eliminating first-paint FOUC.
func ResolveLanguage(r *http.Request) string {
	if q := r.URL.Query().Get("lang"); IsValid(q) {
		return q
	}
	if c, err := r.Cookie("nas-doctor-lang"); err == nil && IsValid(c.Value) {
		return c.Value
	}
	if r.Header != nil {
		supported := Supported()
		for _, a := range parseAcceptLanguage(r.Header.Get("Accept-Language")) {
			la := strings.ToLower(a)
			for _, s := range supported {
				if strings.EqualFold(a, s) {
					return s
				}
			}
			// prefix match: "en-US" -> "en"
			for _, s := range supported {
				if strings.HasPrefix(la, strings.ToLower(s)+"-") {
					return s
				}
			}
		}
	}
	return DefaultLang
}

// parseAcceptLanguage splits an Accept-Language header into language tags
// in priority order, stripping quality factors.
func parseAcceptLanguage(h string) []string {
	if h == "" {
		return nil
	}
	parts := strings.Split(h, ",")
	var out []string
	for _, p := range parts {
		if i := strings.Index(p, ";"); i >= 0 {
			p = p[:i]
		}
		p = strings.TrimSpace(p)
		if p != "" {
			out = append(out, p)
		}
	}
	return out
}

// ServeI18nJS generates the i18n runtime JavaScript for the given language.
// The output is a self-contained IIFE that exposes window.i18n and embeds
// both the requested language dictionary and the English fallback so the
// client can resolve missing keys without a round-trip.
func ServeI18nJS(lang string) ([]byte, error) {
	if !IsValid(lang) {
		lang = DefaultLang
	}
	userDict, err := loadDictionary(lang)
	if err != nil {
		return nil, fmt.Errorf("i18n: load %s: %w", lang, err)
	}
	enDict, err := loadDictionary(DefaultLang)
	if err != nil {
		return nil, fmt.Errorf("i18n: load fallback: %w", err)
	}

	enJSON, _ := json.Marshal(enDict)
	userJSON, _ := json.Marshal(userDict)

	var b strings.Builder
	b.WriteString("(function(global){\n\"use strict\";\n")
	b.WriteString("var dictionaries={\n")
	b.WriteString("\"en\":" + string(enJSON))
	if lang != DefaultLang {
		b.WriteString(",\n\"" + lang + "\":" + string(userJSON))
	}
	b.WriteString("\n};\n")
	b.WriteString("var fallbackLang=\"en\";\n")
	b.WriteString("var currentLang=" + fmt.Sprintf("%q", lang) + ";\n")
	b.WriteString("var listeners=[];\n")
	b.WriteString(runtimeBody)
	b.WriteString("\n})(window);\n")
	return []byte(b.String()), nil
}

// runtimeBody is the language-agnostic client-side i18n runtime. It is
// concatenated after the dictionaries are injected above.
//
// Supported attributes:
//   - data-i18n="key"            → textContent
//   - data-i18n-html="key"       → innerHTML (use for text containing entities)
//   - data-i18n-attr="attr:key"  → set a single attribute
//     (comma-separated for multiple: data-i18n-attr="title:foo,placeholder:bar")
const runtimeBody = `document.documentElement.style.visibility="hidden";
function lookup(dict,key){return dict&&Object.prototype.hasOwnProperty.call(dict,key)?dict[key]:null;}
function notifyListeners(lang){for(var i=0;i<listeners.length;i++){try{listeners[i](lang);}catch(e){if(console&&console.error)console.error(e);}}}
global.dictionaries=dictionaries;
global.i18n={
getLanguage:function(){return currentLang;},
setLanguage:function(lang){
  if(dictionaries[lang]){
    currentLang=lang;
    try{document.documentElement.lang=lang;}catch(e){}
    notifyListeners(lang);
  }else if(typeof console!=="undefined"&&console.warn){
    console.warn("[i18n] unsupported language:",lang);
  }
},
t:function(key,params){
  var text=lookup(dictionaries[currentLang],key);
  if(text===null){text=lookup(dictionaries[fallbackLang],key);}
  if(text===null){
    if(typeof console!=="undefined"&&console.warn){console.warn("[i18n] missing key:",key);}
    return key;
  }
  if(params){
    for(var k in params){
      if(Object.prototype.hasOwnProperty.call(params,k)){
        text=text.replace(new RegExp("{{"+k+"}}","g"),params[k]);
      }
    }
  }
  return text;
},
translateDOM:function(root){
  var rootNode=root||document;
  var i,el,key;
  var textNodes=rootNode.querySelectorAll("[data-i18n]");
  for(i=0;i<textNodes.length;i++){
    el=textNodes[i];key=el.getAttribute("data-i18n");
    if(key){el.textContent=this.t(key);}
  }
  var htmlNodes=rootNode.querySelectorAll("[data-i18n-html]");
  for(i=0;i<htmlNodes.length;i++){
    el=htmlNodes[i];key=el.getAttribute("data-i18n-html");
    if(key){el.innerHTML=this.t(key);}
  }
  var attrNodes=rootNode.querySelectorAll("[data-i18n-attr]");
  for(i=0;i<attrNodes.length;i++){
    el=attrNodes[i];var spec=el.getAttribute("data-i18n-attr");
    if(!spec)continue;
    var pairs=spec.split(",");
    for(var p=0;p<pairs.length;p++){
      var pair=pairs[p].split(":");
      if(pair.length===2){el.setAttribute(pair[0].trim(),this.t(pair[1].trim()));}
    }
  }
},
onLanguageChange:function(fn){listeners.push(fn);},
translateFinding:function(f,field){
  if(!f||!f.finding_type||!f[field])return f?(f[field]||""):"";
  var key='finding.'+f.finding_type+'.'+field;
  var tmpl=this.t(key);
  if(tmpl===key)return f[field]||"";
  var orig=f[field];
  var result=tmpl;
  var enTmpl=dictionaries['en']?dictionaries['en'][key]:null;
  if(!enTmpl)return result;
  var paramMatches=enTmpl.match(/\{\{(\w+)\}\}/g);
  if(!paramMatches||paramMatches.length===0)return result;
  var parts=enTmpl.split(/(\{\{\w+\}\})/);
  var regexStr='';
  for(var pi=0;pi<parts.length;pi++){
    if(/^\{\{\w+\}\}$/.test(parts[pi])){regexStr+='([\\s\\S]*?)';}
    else if(parts[pi]){regexStr+=parts[pi].replace(/[.*+?^${}()|[\]\\]/g,'\\$&');}
  }
  try{
    var m=orig.match(new RegExp('^'+regexStr));
    if(m){
      for(var pi2=0;pi2<paramMatches.length&&pi2<m.length-1;pi2++){
        var pname=paramMatches[pi2].replace(/\{\{|\}\}/g,'');
        result=result.replace('{{'+pname+'}}',m[pi2+1]);
      }
    }
  }catch(e){}
  // Translate tier labels (e.g. "Occasional — likely transient") injected
  // as {{tier}} params from backend analyzer. Only 4 known tiers, so a
  // simple scan over finding.tier.* keys is cheap enough.
  var tierPrefix='finding.tier.';
  var enDict=dictionaries['en']||{};
  for(var tk in enDict){
    if(tk.indexOf(tierPrefix)===0){
      var enTier=enDict[tk];
      var trTier=this.t(tk);
      if(trTier!==tk&&enTier!==trTier&&result.indexOf(enTier)!==-1){
        result=result.split(enTier).join(trTier);
      }
    }
  }
  return result;
}
};
document.addEventListener("DOMContentLoaded",function(){global.i18n.translateDOM();document.documentElement.style.visibility="visible";});
setTimeout(function(){document.documentElement.style.visibility="visible";},1500);`
