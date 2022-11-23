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
</style>
