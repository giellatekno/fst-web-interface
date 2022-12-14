<script>
    import { t } from "svelte-intl-precompile";
    import { Pulse } from "svelte-loading-spinners";
    import { lang } from "../lib/stores.js";
    import { paradigm } from "../lib/api.js";
    import WordInput from "../components/WordInput.svelte";
    import RadioGroup from "../components/RadioGroup.svelte";

    let value = "";
    let word_class = "Any";
    let size = "Standard";
    const word_class_choices = ["Any", "Noun", "Verb", "Adjective", "Adverb", "Pronoun", "Numeral"];
    const paradigm_sizes = ["Minimal", "Standard", "Full"];
    $: results = get_results(value, word_class, size);

    $: usage = $t(`usage.lang.${$lang}`);

    function get_results(value, word_class, size) {
        if (!value) return null;
        const word_class_idx = word_class_choices.findIndex(el => el === word_class);
        const size_idx = paradigm_sizes.findIndex(el => el === size);
        return paradigm($lang, value, word_class_idx, size_idx);
    }
</script>

<main>
    <h1>[l6e] Paradigm</h1>
    <p>{@html usage}</p>

    <RadioGroup header="Word class" bind:selected={word_class} choices={word_class_choices} />
    <RadioGroup header="Paradigmestørrelse" bind:selected={size} choices={paradigm_sizes} />

    <WordInput
        debounce={1000}
        on:new-value={({ detail }) => value = detail}
        on:reset-value={({ detail }) => value = detail}
        on:new-input-started={({ detail }) => value = ""}
    />

    {#if results}
        {#await results}
            <Pulse color="#FF0000" size="28" unit="px" duration="1s" />
        {:then res}
            {#if res.result}
                <table>
                    {#each res.result as [tags, word]}
                        <tr>
                            <td>{tags}</td>
                            <td>{word}</td>
                        </tr>
                    {:else}
                        <tr><td>(no results found)</td></tr>
                    {/each}
                </table>
            {:else}
                {res.error}
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
