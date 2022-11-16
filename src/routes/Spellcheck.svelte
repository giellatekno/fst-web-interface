<script>
    import { spell } from "../lib/api.js";
    import { lang } from "../lib/stores.js";

    const EXAMPLE_RESPONSE = {"text":"viessu","results":[{"word":"viessu","is_correct":true,"suggestions":[{"value":"viessu","weight":11.383789},{"value":"viesu","weight":19.28125},{"value":"vieso","weight":29.3018},{"value":"viessot","weight":36.3018},{"value":"viisso","weight":36.3018},{"value":"visso","weight":36.3018},{"value":"beassu","weight":48.3018},{"value":"geassu","weight":48.3018},{"value":"meassu","weight":48.3018},{"value":"seassu","weight":48.3018}]}]};

    let search = "";
    //let results = "";
    //let results = Promise.reject(null);
    let results = Promise.resolve(EXAMPLE_RESPONSE.results);

    /*
    $: results =
        debounce(search, 1000)
        .then(search_term => {
            return spell(
                $lang,
                search_term
            );
        });
        */

    $: console.log(results);
    function do_query() {
        console.log("do query now");
        results = spell($lang, search);
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

</script>

<h1>[l6e]Spellchecker</h1>

<p>[l6e] Skriv inn et ord for å få stavekontroll.</p>

<input bind:value={search} />
<button on:click={do_query}>[l6e] Sjekk</button>

{#await results}
    venter...
{:then words}
    <div style="display: flex;">
    {#each words as { word, is_correct, suggestions }}
        <div class="single-result">
            <span
                class="result-word"
                class:is_correct>{word}</span>
            <br>

            Lignende ord:
            <ul class="suggestions">
                {#if suggestions.length}
                    {#each suggestions as { value: sugg }}
                        <li>{sugg}</li>
                    {/each}
                {:else}
                    <li class="nosugg">
                        Ingen lignende ord funnet.
                    </li>
                {/if}
            </ul>
        </div>
    {/each}
    </div>
{:catch err}
    {#if err === null}
        [DEBUG] search term is empty
    {:else if !err.message.startsWith("ValueError")}
        {err}
    {/if}
{/await}

<style>
    input {
        padding: 12px 18px;
        font-size: 1.6em;
        border: 1px solid black;
        border-radius: 12px;
        width: 8em;
    }

    div.single-result {
        display: block;
    }

    span.result-word {
        display: inline-block;
        color: red;
        padding: 12px 18px;
        font-size: 1.5em;
    }

    span.result-word.is_correct {
        color: green;
    }

    ul.suggestions {
        list-style: none;
    }

    ul.suggestions > li.nosugg {
        font-style: italic;
    }
</style>
