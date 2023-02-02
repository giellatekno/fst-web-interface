<script>
    import { t } from "svelte-intl-precompile";
    import { Pulse } from "svelte-loading-spinners";
    import { lang } from "../lib/stores.js";
    import { num } from "../lib/api.js";
    import WordInput from "../components/WordInput.svelte";

    let results = [];

    $: usage = $t(`usage.lang.${$lang}`);

    async function on_new_value({ detail: value }) {
        results.unshift(num($lang, value));
        results = results;
    }
</script>

<main>
    <span>
        <h1>[l6e] {$t("num")}</h1>
        <a href="/{$lang}">[l6e] Tilbake til verktøy</a>
    </span>

    <p>{@html usage}</p>

    <form>
        <WordInput
            debounce={1000}
            on:new-value={on_new_value}
            on:new-input-started={() => {}}
            on:reset-value={() => results = []}
        />
    </form>

    <table>
        {#each results as result}
            <tr>
                {#await result}
                    <td colspan="2">
                        <Pulse color="#FF0000" size="28" unit="px" duration="1s" />
                    </td>
                {:then res}
                    <td>{res.number}</td>
                    <td>
                        {#each res.answers as text}
                            {text}<br>
                        {/each}
                    </td>
                {/await}
            </tr>
        {/each}
    </table>
</main>

<style>
    main {
        margin-left: 34px;
    }

    h1 {
        display: inline-block;
        padding-right: 1em;
        padding-bottom: 0;
        margin-bottom: 0;
    }

    td {
        padding: 6px;
    }

    tr > td:first-of-type {
        vertical-align: top;
    }
</style>
