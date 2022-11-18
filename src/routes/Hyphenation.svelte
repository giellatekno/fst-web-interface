<script>
    import { t } from "svelte-intl-precompile";
    import { Pulse } from "svelte-loading-spinners";
    import { lang } from "../lib/stores.js";
    import { hyphenate } from "../lib/api.js";
    import WordInput from "../components/WordInput.svelte";

    let value = "";
    let input;

    let results = [
        { word: "fattig", promise: Promise.resolve(["fat-tig"]) },
        { word: "farsdag", promise: Promise.resolve(["fars-dag"]) },
        { word: "bursdag", promise: Promise.resolve(["burs-dag"]) },
    ];
    $: usage = $t(`usage.lang.${$lang}`);
    $: debounce(value, 1000).then(search_and_update);

    async function search_and_update(word) {
        if (word === null) return;
        const new_result = {
            word: word,
            promise: hyphenate($lang, word),
        };
        results.splice(0, 0, new_result);
        results = results;
    }

    let _timer;
    let _promise;
    function debounce(s, ms) {
        if (_timer) {
            window.clearTimeout(_timer);
            _timer = null;
        }

        if (!s) return Promise.resolve(null);

        _promise = new Promise(resolve => {
            _timer = window.setTimeout(
                () => resolve(s), ms);
        });

        return _promise;
    }

    function pp_result(res) {
        return res.replaceAll("-", '<span style="color: red;"> &#8212; </span>');
    }

    function empty_query() {
        value = "";
        input.focus();
    }

    function reset() {
        value = "";
        results = [];
        input.focus();
    }
</script>

<main>
    <h1>[l6e] Hyphenation</h1>
    <p>{@html usage}</p>

    <form>
        <WordInput bind:this={input} bind:value />
        <button on:click|preventDefault={empty_query}>[l6e] Nytt søk</button>
        <button on:click|preventDefault={reset}>[l6e] Nullstill</button>
    </form>

    <table class="results">
        {#each results as { word, promise }}
            <tr>
                <td>{word}</td>
                <td>
                    {#await promise}
                        <Pulse color="#FF0000" size="28" unit="px" duration="1s" />
                    {:then result_array}
                        {#each result_array as answer}
                            {@html pp_result(answer)}
                            <br>
                        {/each}
                    {:catch err}
                        FEIL: {err}
                    {/await}
                </td>
        {/each}
    </table>

    <!--
    {#await results}
    {:then values}
        {#if values.length}
            {#each values as v}
                {@html pp_result(v)}
            {/each}
        {:else}
            Fant ingen resultater.
        {/if}
    {:catch err}
        {#if !err.message.startsWith("ValueError")}
            {err}
        {:else}
        {/if}
    {/await}
    -->
</main>

<style>
    main {
        margin-left: 34px;
    }

    table.results {
        /*margin-right: 34px;*/
    }
    
    table.results tr:first-of-type {
        height: 3em;
        vertical-align: top;
    }

    table.results td {
        padding: 4px 0px;
    }

    table.results td:nth-of-type(2) {
        padding-left: 12px;
    }

    table.results td:first-of-type {
        width: 5em;
    }
</style>
