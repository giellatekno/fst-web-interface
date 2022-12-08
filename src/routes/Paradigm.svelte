<script>
    import { t } from "svelte-intl-precompile";
    import { Pulse } from "svelte-loading-spinners";
    import { lang } from "../lib/stores.js";
    import { paradigm } from "../lib/api.js";
    import WordInput from "../components/WordInput.svelte";

    let results = null;

    $: usage = $t(`usage.lang.${$lang}`);

    function pp_res(res) {
        return JSON.stringify(res.result)
            .slice(1, -1)
            .trim()
            .replaceAll("\\n", "<br>")
            .replaceAll("\\t", "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;");
    }

    function on_new_value({ detail: value }) {
        results = paradigm($lang, value);
    }
</script>

<main>
    <h1>[l6e] Paradigm</h1>
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
            {#if res !== null}
                {@html pp_res(res)}
            {:else}
                tmp: ingen resultat
            {/if}
        {:catch e}
            Error: {e}
        {/await}
    {/if}
</main>

<style>
    main {
        margin-left: 34px;
    }
</style>
