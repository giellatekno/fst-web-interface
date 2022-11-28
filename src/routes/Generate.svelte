<script>
    import { t } from "svelte-intl-precompile";
    import { Pulse } from "svelte-loading-spinners";
    import { lang } from "../lib/stores.js";
    import { generate } from "../lib/api.js";
    import WordInput from "../components/WordInput.svelte";

    let results = null;

    $: usage = get_usage($t, $lang);
    $: introduction = get_introduction($t, $lang);
    $: instruction = get_instruction($t, $lang);
    $: example = get_example($t, $lang);

    function get_usage($t, $lang) {
        const specific_key = `usage.lang.${$lang}`;
        const specific_val = $t(specific_key);
        if (specific_val !== specific_key) {
            return specific_val;
        } else {
            const generic_key = `usage`;
            const generic_val = $t(generic_key);
            return generic_val !== generic_key ? generic_val : "";
        }
    }

    function get_example($t, $lang) {
        const specific_key = `example.tool.generate.lang.${$lang}`;
        const specific_val = $t(specific_key);
        if (specific_val === specific_key) {
            // translation string equals the key if it's not found
            const generic_key = `example.tool.generate`;
            const generic_val = $t(generic_key);
            return generic_key === generic_val ? "" : generic_val;
        } else {
            return specific_val;
        }
    }

    function get_introduction($t, $lang) {
        const specific_key = `introduction.tool.generate.lang.${$lang}`;
        const specific_val = $t(specific_key);
        if (specific_val !== specific_key) {
            return specific_val;
        } else {
            const generic_key = `introduction.tool.generate`;
            const generic_val = $t(generic_key);
            return generic_val !== generic_key ? generic_val : "";
        }
    }

    function get_instruction($t, $lang) {
        const specific_key = `instruction.tool.generate.lang.${$lang}`;
        const specific_val = $t(specific_key);
        if (specific_val !== specific_key) {
            return specific_val;
        } else {
            const generic_key = `instruction.tool.generate`;
            const generic_val = $t(generic_key);
            return generic_val !== generic_key ? generic_val : "";
        }
    }

    function on_new_value({ detail: value }) {
        results = generate($lang, value);
    }
</script>

<main>
    <h1>{$t("generate")}</h1>
    {#if usage}<p>{@html usage}</p>{/if}
    {#if introduction}<p>{@html introduction}</p>{/if}
    {#if instruction}<p>{@html instruction}</p>{/if}
    {#if example}<p>{@html example}</p>{/if}

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
