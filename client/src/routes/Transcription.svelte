<script>
    import { t } from "svelte-intl-precompile";
    import { lang } from "../lib/stores.js";
    import { transcribe } from "../lib/api.js";
    import WordInput from "../components/WordInput.svelte";

    let results = null;

    $: usage = $t(`usage.lang.${$lang}`);

    function appendkey(key) {
        return function(ev) {
            ev.preventDefault();
            value += key;
            input.focus();
        }
    }

    function on_new_value({ detail: value }) {
        results = transcribe($lang, value);
    }
</script>

<main>
    <span>
        <h1>[l6e] {$t("transcribe")}</h1>
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

    {#if results}
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
