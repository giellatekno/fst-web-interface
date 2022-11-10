<script>
    import { t } from "svelte-intl-precompile";
    import {
        tool_langs,
        ui_langs,
        tool_lang_star,
    } from "./lib/config.js";
    import {
        ui_lang,
        target_lang,
    } from "./lib/stores.js";
    import { language_names } from "./lib/natlang.js";
    import Search from "./components/Search.svelte";

    let visible_langs = tool_langs;
    let search = "";

    $: filter_langs(search);
    $: num_langs_shown = search === "" ? 12 : 100;

    function filter_langs(search) {
        if (search === "") {
            visible_langs = tool_langs
                .slice(0, 12);
        } else {
            visible_langs = tool_langs
                .filter(lang =>
                    lang.includes(search));
        }
    }
</script>

<h1>{$t("language tools")}</h1>
<div>
    <h2>Vis verktøy for ...</h2>

    <Search bind:value={search} />

    <blockquote>
        Gullstjerne er våre beste språk, sølv er også ok, for bronsespråkene er verktøyene våre mindre utviklet.
    </blockquote>

    <main>
        {#each visible_langs.slice(0, num_langs_shown) as lang}
            <span class="language"
                on:click={() => $target_lang = lang}>
                <span class="inner">
                    {language_names[$ui_lang][lang]}
                </span>
                <span
                    class="star {tool_lang_star[lang]}"
                >
                    ★
                </span>
            </span>
            <br>
        {:else}
            Ingen treff på søkeordet...
        {/each}
    </main>
    <span>Vis alle...</span>

    <br>
</div>


<style>
    main {
        display: grid;
        width: 800px;
        grid-template-columns: 1fr 1fr 1fr 1fr;
    }

    blockquote {
        margin-left: 0;
        padding: 16px;
        border: 1px solid #fbac59;
        font-style: italic;
        background-color: rgba(221, 157, 36, 0.13);
    }

    h2 {
        display: inline;
        font-size: 1.4em;
        font-weight: normal;
    }

    span.language {
        font-size: 22px;
        padding: 6px;
    }

    span.language > span.inner {
        cursor: pointer;
        color: blue;
        text-decoration: underline;
    }

    span.star {
        font-size: 1.4em;
    }

    span.star.gold {
        color: #ffcb00;
    }

    span.star.silver {
        color: gray;
    }

    span.star.bronze {
        color: red;
    }
</style>
