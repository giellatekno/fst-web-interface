<script>
    import { t } from "svelte-intl-precompile";
    import { Pulse } from "svelte-loading-spinners";
    import { lang } from "../lib/stores.js";
    import { generate } from "../lib/api.js";
    import WordInput from "../components/WordInput.svelte";

    let results = null;

    $: usage = $t(`usage.lang.${$lang}`);

    function on_new_value({ detail: value }) {
        results = generate($lang, value);
    }
</script>

<main>
    <h1>[l6e] Generate</h1>
    <p>{@html usage}</p>
    <p>{$t("introduction.tool.generate")}</p>
    <p>{$t("instruction.tool.generate")}</p>

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
                {JSON.stringify(res)}
            {/if}
        {:catch e}
            Error: e
        {/await}
    {/if}
</main>

<style>
    main {
        margin-left: 34px;
    }
</style>
