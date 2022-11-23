<script>
    import example_img from "../assets/language.svg";
    import spellcheck_img from "../assets/spellcheck.svg";
    import hyphenation_img from "../assets/hyphenation.svg";
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
            "num",
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

    function get_image(tool) {
        switch (tool) {
            case "spellcheck":
                return spellcheck_img;
            case "hyphenation":
                return hyphenation_img;
            default:
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
    main {
        display: grid;
        grid-template-columns: repeat(2, max-content);
        grid-gap: 17px;
        margin: 0 34px;
        /*width: calc(100vw - 68px);*/
    }

    @media screen and (max-width: 768px) {
        main {
            grid-template-columns: 1fr;
        }
    }

    a.tool { 
        display: grid;
        color: black;
        text-decoration: none;
        grid-template-areas:
            'img img title title title'
            'img img desc desc desc';
        grid-template-columns: 42px 42px repeat(3, max-content);
        background-color: #f0eab3;
        border-radius: 12px;
        padding: 4px 12px;
        box-shadow: 4px 4px 12px 0px rgba(121, 121, 89, 0.44);
        transition:
            background-color ease-out 0.25s;
    }

    @media screen and (max-width: 768px) {
        a.tool {
        }
    }

    a.tool:hover {
        background-color: #ece268;
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
        font-size: 1.8em;
        font-weight: 500;
        font-variant: small-caps;
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
