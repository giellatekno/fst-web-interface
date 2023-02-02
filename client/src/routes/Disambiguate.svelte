<script>
    import { t } from "svelte-intl-precompile";
    import { Pulse } from "svelte-loading-spinners";
    import { lang } from "../lib/stores.js";
    import { disambiguate } from "../lib/api.js";
    import WordInput from "../components/WordInput.svelte";

    let results = null;

    $: usage = $t(`usage.lang.${$lang}`);

    function on_new_value({ detail: value }) {
        results = disambiguate($lang, value);
    }
</script>

<main>
    <span>
        <h1>{$t("disambiguate")}</h1>
        <a href="/{$lang}">[l6e] Tilbake til verktøy</a>
    </span>

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
            {#each res as { input_word, word_disambs }}
                <span class="input_word">
                    {input_word}
                </span>
                <br>
                {#each word_disambs as { root_word, classes }}
                    <span class="disamb-line">
                        <span class="root_word">
                            {root_word}
                        </span>
                        <span class="classes">
                            {classes}
                        </span>
                    </span>
                    <br>
                {/each}
            {/each}
        {:catch e}
            Error: {e}
        {/await}
    {/if}
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

    span.input_word {
        color: red;
        font-size: 1.2em;
    }

    span.disamb-line {
        margin-left: 34px;
    }

    span.root_word {
        color: blue;
    }

    span.classes {
        color: green;
    }
</style>
