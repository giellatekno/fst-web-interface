<script>
    import { t } from "svelte-intl-precompile";
    import { Pulse } from "svelte-loading-spinners";
    import { lang } from "../lib/stores.js";
    import { analyze } from "../lib/api.js";
    import WordInput from "../components/WordInput.svelte";

    let results = [];

    $: usage = get_usage($lang, $t);
    $: instruction = $t(`instruction.tool.analyze`);
    $: end = $t(`end.tool.analyze`);

    function get_usage($lang, $t) {
        const lang_specific = $t(`usage.lang.${lang}`);
        if (lang_specific !== `usage.lang.${lang}`) {
            return lang_specific;
        } else {
            const fallback = $t("usage");
            return fallback;
        }
    }

    function on_new_value({ detail: value }) {
        results.unshift(analyze($lang, value));
        results = results;
    }
</script>

<main>
    <span>
        <h1>{$t("analyze")}</h1>
        <a href="/{$lang}">[l6e] Tilbake til verktøy</a>
    </span>

    <p>{@html usage}</p>

    <p>{@html instruction}</p>

    <form>
        <WordInput
            debounce={1000}
            on:new-value={on_new_value}
            on:new-input-started={() => {}}
            on:reset-value={() => results = []}
        />
    </form>

    
    <table>
        {#each results as result}
            {#await result}
                <tr>
                    <td colspan="4">
                        <Pulse color="#FF0000" size="28" unit="px" duration="1s" />
                    </td>
                </tr>
            {:then res}
                    {#each res as { word, root, cls, props }}
                        <tr>
                            <td class="input-word">{word}</td>
                            <td class="root-word">{root}</td>
                            <td class="word-cls">{cls}</td>
                            <td class="word-props">{props}</td>
                        </tr>
                    {/each}
            {:catch e}
                Error: {e}
            {/await}
        {/each}
    </table>

    <p>{@html end}</p>
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

    td.input-word {
        width: 3em;
        color: red;
    }

    td.root-word {
        padding-left: 2em;
        color: green;
    }

    td.word-cls {
        padding-left: 1em;
        text-align: right;
        color: blue;
    }
</style>
