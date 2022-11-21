<script>
    import { t } from "svelte-intl-precompile";
    import { Pulse } from "svelte-loading-spinners";
    import { lang } from "../lib/stores.js";
    import { disambiguate } from "../lib/api.js";
    import WordInput from "../components/WordInput.svelte";

    let value = "";
    let input;

    let results = Promise.resolve("");

    $: usage = $t(`usage.lang.${$lang}`);
    $: debounce(value, 2000).then(search_and_update);

    async function search_and_update(input) {
        if (input === null) return;
        results = disambiguate($lang, input);
    }

    let _timer;
    let _promise;
    function debounce(s, ms) {
        if (_timer) {
            window.clearTimeout(_timer);
            _timer = null;
        }

        if (!s) return Promise.resolve(null);

        _promise = new Promise(resolve => {
            _timer = window.setTimeout(
                () => resolve(s), ms);
        });

        return _promise;
    }

    function empty_query() {
        value = "";
        input.focus();
    }

    function reset() {
        value = "";
        results = [];
        input.focus();
    }
</script>

<main>
    <h1>[l6e] Disambiguate</h1>
    <p>{@html usage}</p>

    <form>
        <WordInput bind:this={input} bind:value />
        <button on:click|preventDefault={empty_query}>[l6e] Nytt søk</button>
        <button on:click|preventDefault={reset}>[l6e] Nullstill</button>
    </form>

    {#await results}
        ...
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
    {/await}
</main>

<style>
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
