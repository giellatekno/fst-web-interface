<script>
    import { t } from "svelte-intl-precompile";
    import { Pulse } from "svelte-loading-spinners";
    import { lang } from "../lib/stores.js";
    import { get_langspecific_key } from "../lib/locales.js";
    import { dependency } from "../lib/api.js";
    import WordInput from "../components/WordInput.svelte";

    let results = null;

    //$: usage = $t(`usage.lang.${$lang}`);
    $: usage = get_langspecific_key("usage", $lang);

    function on_new_value({ detail: value }) {
        results = dependency($lang, value);
    }
</script>

<main>
    <span>
        <h1>{$t("dependency")}</h1>
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
            {#if res}
                {#each res as { word, root, props, dep }}
                    <div class="result">
                        <span class="word">{word}</span>
                        <br>
                        <div class="def">
                            <span class="rootword">{root}</span>
                            <span class="props">{props}</span>
                            <span class="dep">{dep}</span>
                        </div>
                    </div>
                {/each}
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

    div.result {
        font-size: 1.2em;
    }

    div.result > span.word {
        color: red;
    }

    div.result > div.def {
        padding-top: 0.3em;
        margin-left: 3em;
    }

    span.rootword {
        color: blue;
    }

    span.props {
        color: green;
    }

    span.dep {
        color: orange;
    }
</style>
