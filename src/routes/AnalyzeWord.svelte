<script>
    // TODO correct api call
    import { spell } from "../lib/api.js";
    import { lang } from "../lib/stores.js";

    let search = "";
    let results = "";
    let search_term = "";

    $: results =
        debounce(search, 1000)
        .then(search_term => {
            return spell(
                $lang,
                search_term
            );
        });

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

<h1>[l6e]Analyze word tool</h1>

<p>[l6e] Skriv inn ordet du vil ha alle former av</p>

<input bind:value={search} />

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
