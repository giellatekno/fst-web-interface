<script>
    import { t } from "svelte-intl-precompile";
    import { Pulse } from "svelte-loading-spinners";
    import { lang } from "../lib/stores.js";
    import { num } from "../lib/api.js";
    import WordInput from "../components/WordInput.svelte";

    let results = null;

    $: usage = $t(`usage.lang.${$lang}`);

    function on_new_value({ detail: value }) {
        results = num($lang, value);
    }
</script>

<main>
    <h1>[l6e] Num</h1>
    <p>{@html usage}</p>

    <form>
        <WordInput
            debounce={1000}
            on:new-value={on_new_value}
            on:new-input-started={() => results = null}
            on:reset-value={() => results = null}
        />
    </form>

    {#if results}
        {#await results}
            <Pulse color="#FF0000" size="28" unit="px" duration="1s" />
        {:then res}
            <table class="result">
                <tr>
                    <td>{res.number}</td>
                    <td>
                        {#each res.answers as text}
                            {text}<br>
                        {/each}
                    </td>
                </tr>
            </table>
        {:catch e}
            Error: {e}
        {/await}
    {/if}
</main>

<style>
    main {
        margin-left: 34px;
    }

    div.result {
        font-size: 1.2em;
    }

    td {
        padding: 6px;
    }

    tr > td:first-of-type {
        vertical-align: top;
    }

    div.result > span.numbers_as_text {
        margin-left: 34px;
    }
</style>
