<script>
    import { t } from "svelte-intl-precompile";
    import { lang } from "../lib/stores.js";
    import { paradigm } from "../lib/api.js";
    import WordInput from "../components/WordInput.svelte";
    import RadioGroup from "../components/RadioGroup.svelte";

    $: usage = $t(`usage.lang.${$lang}`);

    let input = "";
    let pos = "Any";
    let size = "Standard";
    const poses = {
        Any: "Any",
        Noun: "N",
        Verb: "V",
        Adjective: "Adj",
        Adverb: "Adv",
        Pronoun: "Pron",
    };
    const paradigm_sizes = {
        Minimal: "minimal",
        Standard: "standard",
        Full: "full",
    };

    let paradigm_component;
    let api_data;
    $: update_data(input, pos, $lang, size);

    async function update_data(input, pos, lang, size) {
        if (!input) {
            api_data = null;
            paradigm_component = null;
            return;
        }

        pos = poses[pos];
        api_data = await paradigm(lang, input, pos, paradigm_sizes[size]);

        if (api_data === null) {
            paradigm_component = null;
            return;
        }

        if (pos === "Any") {
            // determine pos from api_data
        } else {
            const path = `../components/paradigm_layouts/${lang}/${pos}.svelte`;
            try {
                const module = await import(path);
                paradigm_component = module.default;
            } catch (e) {
                console.error(`cannot import dynamic module from path ${path}`);
                console.error(e);
                return;
            }
        }
    }
</script>

<main>
    <span>
        <h1>{$t("paradigm")}</h1>
        <a href="/{$lang}">[l6e] Tilbake til verktøy</a>
    </span>

    <p>{@html usage}</p>

    <RadioGroup header="Part of speech" bind:selected={pos} choices={Object.keys(poses)} />
    <RadioGroup header="Paradigmestørrelse" bind:selected={size} choices={Object.keys(paradigm_sizes)} />

    <div style="height: 16px" /> <!-- just for some space -->

    <WordInput
        debounce={1000}
        on:new-value={({ detail }) => { console.log("new input!"); input = detail} }
        on:reset-value={() => input = ""}
        on:new-input-started={() => input = ""}
    />

    <!-- #key makes sure the block reacts when api_data changes -->
    {#key api_data}
        {#if paradigm_component !== null}
            <svelte:component this={paradigm_component} api_data={api_data} />
        {/if}
    {/key}
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
</style>
