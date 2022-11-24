<script>
    import example_img from "../assets/language.svg";
    import spellcheck_img from "../assets/spellcheck.svg";
    import hyphenation_img from "../assets/hyphenation.svg";
    import num_img from "../assets/num.svg";
    import ipa_img from "../assets/ipa.svg";
    import { t } from "svelte-intl-precompile";
    import { locale } from "../lib/locales.js";
    import {
        lang,
        lang_in_locale,
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

    const IMAGES = {
        spellcheck: spellcheck_img,
        hyphenation: hyphenation_img,
        num: num_img,
        transcription: ipa_img,
    }

    $: tools = tools_for($lang);
</script>

<main>
    <h2>Tilgjengelige verktøy for {$lang_in_locale}</h2>

    <div class="tools-wrapper">
        {#each tools as tool}
            <a href="/{$lang}/{tool}" class="tool">
                <img src={IMAGES[tool] || example_img} alt="">
                <span class="title">{$t(tool)}</span>
                <span class="desc">
                    {@html $t(tool + ".description")}
                </span>
            </a>
        {/each}
    </div>

    <p>
        Andre ressurser for {$lang_in_locale}
    </p>

    <a href="#">Direktelenke for denne siden</a>
</main>


<style>
    main {
        margin-left: 34px;
    }

    div.tools-wrapper {
        display: grid;
        grid-template-columns: repeat(2, max-content);
        grid-gap: 17px;
        margin: 0 34px;
        /*width: calc(100vw - 68px);*/
    }

    @media screen and (max-width: 768px) {
        div.tools-wrapper {
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
        grid-template-columns: 35px 35px repeat(3, max-content);
        background-color: #f0e89e;
        border-radius: 4px;
        padding: 4px 12px;
        box-shadow: 2px 2px 4px 0px rgba(121, 121, 89, 0.44);
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
        height: 68px;
        width: 68px;
    }

    a.tool > span.title {
        margin-left: 10px;
        justify-self: start;
        align-self: end;
        grid-area: title;
        font-size: 1.6em;
        font-weight: 500;
        font-variant: small-caps;
        margin-bottom: 6px;
    }

    a.tool > span.desc {
        margin-left: 12px;
        justify-self: start;
        align-self: start;
        grid-area: desc;
        font-style: italic;
        font-size: 1.05em;
    }
</style>
