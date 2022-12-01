# source readme

## How the client svelte app is structured

Some files are located in the project root (_not_ in this src/ folder), and they are
indicated by their paths starting with "../" in this document.

| filepath | description |
|--|--|
|../index.html |Static skeleton index, whose only job is to load main.js |
|../locales/ | locale folder|
|../locales/{eng\|fin\|nob\|rus\|sme}.json|compiled localization strings used by the app|
|../locales/README | short readme of localization|
|../locales/data/ | localization sources (the original .xmls)|
|../locales/xmltojson.py||
|../locales/make_final.py | scripts to compile all relevant .xml files into one .json file per language|
|--|--|
|app.css | global css (for now mostly empty. should add common global css)|
|App.svelte | Application root. Shows the main layout, and any child component|
|main.js | app entrypoint, instantiates App (root) component from App.svelte|
|--|--|
|assets/ | assets folder. images.|
|components/ | common components that are used by other pages|
|lib/ | folder for common javascript files that are included by components|
|lib/api.js | wrappers around fetch() for calling APIs|
|lib/langs.js | different language lists, and also listings of tools. which tool is available for which language is also defined here|
|lib/locales.js | handling of localization. the different *.json localization data from ../locales are loaded here, for example|
|lib/stores.js | various svelte stores. which language and tool the user is exploring is defined here|
|--|--|
|routes/ | route components. these will be loaded by the App.svelte file when the user visits the various different urls.|
|routes/Index.svelte | the page where the user selects which language they want to explore|
|routes/ToolsIndex.svelte | the page where the user selects which tool they want to explore|
|routes/... | the rest of the files in this folder correspond to the various tools.|


