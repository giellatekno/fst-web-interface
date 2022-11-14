<script>
    import { t } from "svelte-intl-precompile";
    import { locale } from "../lib/locales.js";
    import {
        langs,
        language_names,
        lang_star,
    } from "../lib/langs.js";
    import { lang } from "../lib/stores.js";
    import Search from "../components/Search.svelte";

    let visible_langs = langs;
    let search = "";
    let show_all = false;

    $: visible_langs = show_all ? langs : filter_langs(search);

    function filter_langs(search) {
        if (search === "") {
            return langs.slice(0, 12);
        } else {
            return langs.filter(lang =>
                    lang.includes(search));
        }
    }

    function toggle_show_all() {
        show_all = !show_all;
    }
</script>

<h1>{$t("language tools")}</h1>
<div>
    <h2>[l6e] Vis verktøy for ...</h2>

    <Search bind:value={search} />

    <blockquote>
        [l6e] Gullstjerne er våre beste språk, sølv er også ok, for bronsespråkene er verktøyene våre mindre utviklet.
    </blockquote>

    <main>
        {#each visible_langs as lng}
            <span class="language">
                <a href="/{lng}">
                    {language_names[$locale][lng]}
                </a>
                <span
                    class="star {lang_star[lng]}"
                >
                    ★
                </span>
            </span>
            <br>
        {:else}
            [l6e] Ingen treff på søkeordet...
        {/each}
    </main>
    <span on:click={toggle_show_all}>
        {#if show_all}
            [l6e] Vis færre
        {:else}
            [l6e] Vis alle...
        {/if}
    </span>
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
