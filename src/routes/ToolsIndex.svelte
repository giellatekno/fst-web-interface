<script>
    import example_img from "../assets/language.svg";
    import spellcheck from "../assets/spellcheck.svg";
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

    const IMAGES = {
        spellcheck: spellcheck
    };

    function get_image(tool) {
        if (tool === "spellcheck") {
            return spellcheck;
        } else {
            return example_img;
        }
    }

    $: tools = tools_for($lang);
    $: x = language_names[$locale][$lang];
</script>

<h2>Tilgjengelige verktøy for {x}</h2>
<main>
    {#each tools as tool}
        <a href="/{$lang}/{tool}" class="tool">
            <img src={get_image(tool)} alt="">
            <span class="title">{$t(tool)}</span>
            <span class="desc">
                {@html $t(tool + ".description")}
            </span>
        </a>
    {/each}
</main>

<p>
Andre ressurser for {x}
</p>

<a href="#">Direktelenke for denne siden</a>

<style>
    a.tool { 
        display: grid;
        color: black;
        text-decoration: none;
        grid-template-areas:
            'img img title title title'
            'img img desc desc desc';
        grid-template-columns: 42px 42px repeat(3, 1fr);
        background-color: #efedd1;
        border-radius: 8px;
        margin: 12px;
        height: 80px;
        padding: 4px 12px;
        transition:
            background-color ease-in 0.3s;
    }

    a.tool:hover {
        background-color: #ede8a7;
    }

    a.tool > img {
        align-self: center;
        grid-area: img;
        height: 78px;
        width: 78px;
    }

    a.tool > span.title {
        justify-self: start;
        align-self: end;
        grid-area: title;
        font-size: 1.9em;
        margin-bottom: 6px;
    }

    a.tool > span.desc {
        justify-self: start;
        align-self: start;
        grid-area: desc;
        font-style: italic;
        font-size: 1.3em;
    }
</style>
