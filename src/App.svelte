<script>
  import language from "./assets/language.svg";
  import Index from "./Index.svelte";
  import Tools from "./Tools.svelte";

  let page = "index";
  let target_lang = "";

  let selecting_language = false;
  let more_languages = false;
  function select_langauge() {
    selecting_language = !selecting_language;
  }

  function show_more_languages() {
    num_langs_shown = langs.length;
  }

  function on_pagechange(ev) {
    page = "tools";
    target_lang = ev.detail;
  }
</script>

<main>
  <div>
    <img alt="Innholdspråk" on:click={select_langauge} src={language} height="16" />
    {#if selecting_language}
	    <select>
	      {#each ui_langs as lang}
		<option>{lang}</option>
	      {/each}
	    </select>
	    {/if}
  </div>

  {#if page === "index"}
    <Index on:changepage={on_pagechange} />
  {:else if page === "tools"}
    <Tools lang={target_lang} />
  {/if}
</main>


<style>
/*
  .logo {
    height: 6em;
    padding: 1.5em;
    will-change: filter;
  }
  .logo:hover {
    filter: drop-shadow(0 0 2em #646cffaa);
  }
  .logo.svelte:hover {
    filter: drop-shadow(0 0 2em #ff3e00aa);
  }
  .read-the-docs {
    color: #888;
  }
  */

  span.link {
  cursor: pointer;
    text-decoration: underline;
    color: blue;
  }
  div.big {
    margin-left: 18px;
    font-size: 18px;
    }
  div.small {
    margin-left: 18px;
    font-size: 14px;
    }
</style>
