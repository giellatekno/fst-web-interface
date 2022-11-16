<script>
    import { t } from "svelte-intl-precompile";
    import { locale } from "../lib/locales.js";
    import {
        lang,
    } from "../lib/stores.js";
    import {
        language_names,
        analysis_langs,
        paradigm_langs,
        generation_langs,
    } from "../lib/langs.js";

    // Which tools are available for the
    // target language?
    function tools_for(lang) {
        const list = [];

        if (generation_langs.has(lang)) {
            list.push("generate");
        }
        if (analysis_langs.has(lang)) {
            list.push("analyze");
        }
        if (paradigm_langs.has(lang)) {
            list.push("paradigm");
        }

        // others, static for now
        list.push(
            //"generate",
            //"analyze",
            "spellcheck",
            "disambiguate",
            "dependency",
            "hyphenation",
            "transcription",
            //"ortography",
            //"tallordsgenerator",
            //"stedsnavnsordbok",
        );
        return list;
    }

    $: tools = tools_for($lang);
    $: x = language_names[$locale][$lang];
</script>

<h2>Tilgjengelige verktøy for {x}</h2>
<main>
    {#each tools as tool}
        <div class="tool">
            <a
                class="title"
                href="/{$lang}/{tool}"
            >
                {$t(tool)}
            </a>
            <br/>
            <span class="desc">
                {@html $t(tool + ".description")}
            </span>
        </div>
    {/each}
</main>

<p>
Andre ressurser for {x}
</p>

<a href="#">Direktelenke for denne siden</a>

<style>
    div.tool { 
        margin: 12px;
    }

    div.tool > a.title {
        font-size: 1.1em;
        margin-bottom: 6px;
    }

    div.tool > span.desc {
        font-style: italic;
        margin-left: 3em;
    }
</style>
