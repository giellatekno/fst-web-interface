<script>
    import { t } from "svelte-intl-precompile";
    import { lang } from "../lib/stores.js";
    import { transcribe } from "../lib/api.js";
    import WordInput from "../components/WordInput.svelte";
    let value = "";

    $: usage = $t(`usage.lang.${$lang}`);
    $: results =
        debounce(value, 1000)
        .then(word => transcribe($lang, word));

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

    function appendkey(key) {
        return function(ev) {
            ev.preventDefault();
            value += key;
            input.focus();
        }
    }
    let input;
</script>

<main>
    <h1>[l6e] IPA Transcribe</h1>
    <p>{@html usage}</p>

    <form>
        <WordInput bind:this={input} bind:value />
        <br>
        <button
            class="key"
            on:click={appendkey("æ")}>
            æ
        </button>
        <button
            class="key"
            on:click={appendkey("ø")}>
            ø
        </button>
        <button
            class="key"
            on:click={appendkey("å")}>
            å
        </button>
    </form>

    {#await results}
        [spinner]...
    {:then values}
        {#if values.length}
            <div class="results">
            {#each values as v}
                {v}<br>
            {/each}
            </div>
        {:else}
            [l6e] Fant ingen resultater.
        {/if}
    {:catch err}
        {#if !err.message.startsWith("ValueError")}
            {err}
        {:else}
            [DEBUG] search term is empty
        {/if}
    {/await}
</main>

<style>
    main {
        margin-right: 34px;
    }

    button.key {
        padding: 2px 0;
        font-size: 1.4em;
        font-family: monospace;
        border: 1px solid #667;
        background-color: #f8f8f8;
        background:
            radial-gradient(circle at 8px 8px, #f8f8f8 80%, #888 90%);
        border-radius: 4px;
        width: 1.7em;
        box-shadow: 0.8px 0.8px 0px 0px #778;
        box-sizing: border-box;
    }

    div.results {
        margin: 26px;
    }
</style>
