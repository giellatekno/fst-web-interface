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
    {JSON.stringify(values)}
{:catch err}
    {#if !err.message.startsWith("ValueError")}
        {err}
    {:else}
        [DEBUG] search term is empty
    {/if}
{/await}
