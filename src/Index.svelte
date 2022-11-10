<script>
    import { t } from "svelte-intl-precompile";
    import {
        tool_langs,
        ui_langs,
    } from "./lib/config.js";
    import {
      target_lang,
    } from "./lib/stores.js";
    import Search from "./components/Search.svelte";

    let visible_langs = tool_langs;
    let num_langs_shown = 5;
    let search = "";

    $: filter_langs(search);
    $: num_langs_shown = search === "" ? 5 : 100;

    function filter_langs(search) {
        if (search === "") {
            visible_langs = tool_langs
                .slice(0, 5);
        } else {
            visible_langs = tool_langs
                .filter(lang =>
                    lang.includes(search));
        }
    }
</script>

<h1>{$t("language tools")}</h1>
<div>
    <span>Vis verktøy for ...</span>
    <Search bind:value={search} />
    <br>
    {#each visible_langs.slice(0, num_langs_shown) as lang}
        <span
            on:click={() => $target_lang = lang}>
            {lang}
        </span>
        <br>
    {:else}
        Ingen treff på søkeordet...
    {/each}
    <span>Vis alle...</span>

    <br>
</div>
