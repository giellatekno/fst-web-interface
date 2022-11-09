<script>
  import { createEventDispatcher } from "svelte";
  const dispatch = createEventDispatcher();

  import { tool_langs, ui_langs } from "./lib/config.js";

  let visible_langs = tool_langs;
  let num_langs_shown = 5;
  let search = "";

  $: filter_langs(search);
  $: num_langs_shown = search === "" ? 5 : 100;

  function choose_lang(lang) {
    dispatch("changepage", lang);
  }

  function filter_langs(search) {
     if (search === "") {
       visible_langs = tool_langs.slice(0, 5);
     } else {
       visible_langs = tool_langs.filter(lang => lang.includes(search));
     }
  }
</script>


  <h1>Språkverktøy</h1>
  <div>
    <span>Vis verktøy for ...</span>
    <input bind:value={search} placeholder="søk..."/>
    {#each visible_langs.slice(0, num_langs_shown) as lang}
      <div on:click={() => choose_lang(lang)}>{lang}</div>
    {:else}
      Ingen treff på søkeordet...
    {/each}
    <span>Vis alle...</span>

    <br>
  </div>
