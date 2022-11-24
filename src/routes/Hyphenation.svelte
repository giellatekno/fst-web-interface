<script>
    import { t } from "svelte-intl-precompile";
    import { Pulse } from "svelte-loading-spinners";
    import { lang } from "../lib/stores.js";
    import { hyphenate } from "../lib/api.js";
    import WordInput from "../components/WordInput.svelte";

    let results = [
        { word: "fattig", promise: Promise.resolve(["fat-tig"]) },
        { word: "farsdag", promise: Promise.resolve(["fars-dag"]) },
        { word: "bursdag", promise: Promise.resolve(["burs-dag"]) },
    ];

    $: usage = $t(`usage.lang.${$lang}`);

    function pp_result(res) {
        return res.replaceAll("-", '<span style="color: red;"> &#8212; </span>');
    }

    function on_new_value({ detail: value }) {
        const new_result = {
            word: value,
            promise: hyphenate($lang, value),
        };
        results.splice(0, 0, new_result);
        results = results;
    }
</script>

<main>
    <h1>[l6e] Hyphenation</h1>
    <p>{@html usage}</p>

    <form>
        <WordInput
            debounce={1000}
            on:new-value={on_new_value}
        />
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

    <div style="margin-top: 3em;">
        <p class="langmodel-info">
            Språkmodellen ble sist oppdatert DATO &mdash;&nbsp;<code>commit 0c36f5c,
                    <a rel="external"
                       href="https://github.com/giellalt/lang-{$lang}"
                    >github.com/giellalt/lang-{$lang}</a></code>
        </p>
    </div>
</main>

<style>
    main {
        margin-left: 34px;
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

    p.langmodel-info {
        /*
        display: inline;
        font-size: 0.88em;
        padding: 10px;
        border-left: 8px solid #e39541;
        background-color: #f7e3aa;
        border-top-right-radius: 4px;
        border-top-left-radius: 2px;
        border-bottom-left-radius: 1px;
        box-shadow: 1px 2px 3px 0 #d59441;
        */

        display: inline;
        font-size: 0.85em;
        padding: 8px 10px;
        border: 2px solid #d9d914;
        background-color: #f4f49c;
    }

    p.langmodel-info,
    p.langmodel-info a,
    p.langmodel-info code {
        color: #111;
    }
</style>
