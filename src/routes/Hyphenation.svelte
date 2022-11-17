<script>
    import { t } from "svelte-intl-precompile";
    import { lang } from "../lib/stores.js";
    import { hyphenate } from "../lib/api.js";

    let value = "";

    function do_query() {
        console.log("doing query with input:", value);
    }

    $: usage = $t(`usage.lang.${$lang}`);
    $: results =
        debounce(value, 1000)
        .then(word => hyphenate($lang, word));

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

    function pp_result(res) {
        return res.replaceAll("-", '<span style="color: red;"> &#8212; </span>');
    }
</script>

<h1>[l6e] Hyphenation</h1>
<p>{@html usage}</p>

<form>
    <input bind:value>
    <button type="submit" on:click|preventDefault={do_query}>[l6e] Hyphenate</button>
</form>

{#await results}
    venter...
{:then values}
    {#if values.length}
        {#each values as v}
            {@html pp_result(v)}
        {/each}
    {:else}
        Fant ingen resultater.
    {/if}
{:catch err}
    {#if !err.message.startsWith("ValueError")}
        {err}
    {:else}
        [DEBUG] search term is empty
    {/if}
{/await}

<style>
    span.result {
        /* TEMP */
        margin: 34px;

        font-size: 1.4em;
    }
</style>
