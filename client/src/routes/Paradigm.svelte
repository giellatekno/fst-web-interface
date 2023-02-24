<script>
    import { t } from "svelte-intl-precompile";
    import { lang } from "../lib/stores.js";
    import { paradigm } from "../lib/api.js";
    import WordInput from "../components/WordInput.svelte";
    import RadioGroup from "../components/RadioGroup.svelte";
    import ParadigmTable from "../components/ParadigmTable.svelte";

    let input = "";
    let word_class = "Any";
    let size = "Standard";
    const word_classes = {
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
    $: xx = get_results(input, word_class, size);
    $: results = xx.results;

    $: usage = $t(`usage.lang.${$lang}`);

    async function get_results(input, word_class, size) {
        if (!input) return null;
        word_class = word_classes[word_class];
        const mode = paradigm_sizes[size];
        const api_result = await paradigm($lang, input, word_class, mode);
        console.log(api_result);
        if (Array.isArray(api_result)) {
            return { pos: { results: api_result, primary: true } };
        } else {
            console.log("api result not an array, assuming object");
            console.log("typeof", typeof api_result);
            // find primary
            let res = {};
            const others = [];
            for (const [pos, entry] of Object.entries(api_result)) {
                if (entry.primary) {
                    res[pos] = { results: entry.results, primary: true };
                } else {
                    // push this pos
                    others.push(pos);
                }
            }

            return res;
        }
    }
</script>

<main>
    <span>
        <h1>{$t("paradigm")}</h1>
        <a href="/{$lang}">[l6e] Tilbake til verktøy</a>
    </span>

    <p>{@html usage}</p>

    <RadioGroup header="Word class" bind:selected={word_class} choices={Object.keys(word_classes)} />
    <RadioGroup header="Paradigmestørrelse" bind:selected={size} choices={Object.keys(paradigm_sizes)} />

    <div style="height: 16px" /> <!-- just for some space -->

    <WordInput
        debounce={1000}
        on:new-value={({ detail }) => input = detail}
        on:reset-value={() => input = ""}
        on:new-input-started={() => input = ""}
    />

    <ParadigmTable data={results} />
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
