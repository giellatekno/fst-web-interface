<script>
    import { t } from "svelte-intl-precompile";
    import { Pulse } from "svelte-loading-spinners";
    import { lang } from "../lib/stores.js";
    import { paradigm } from "../lib/api.js";
    import WordInput from "../components/WordInput.svelte";

    let value = "";
    let input;
    let results = Promise.resolve(null);

    $: usage = $t(`usage.lang.${$lang}`);
    $: debounce(value, 1000)
        .then(search_and_update);

    async function search_and_update(input) {
        if (input === null) return;
        results = paradigm($lang, input);
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
        results = Promise.resolve(null);
        input.focus();
    }
</script>

<main>
    <h1>[l6e] Paradigm</h1>
    <p>{@html usage}</p>

    <form>
        <WordInput bind:this={input} bind:value />
        <button on:click|preventDefault={empty_query}>[l6e] Nytt søk</button>
        <button on:click|preventDefault={reset}>[l6e] Nullstill</button>
    </form>

    {#await results}
        ...
    {:then res}
        {#if res !== null}
            {JSON.stringify(res)}
        {/if}
    {:catch e}
        Feil: {e}
    {/await}
</main>
