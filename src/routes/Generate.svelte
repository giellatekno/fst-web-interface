<script>
    import { t } from "svelte-intl-precompile";

    let value = "";

    function do_query() {
        console.log("doing query with input:", value);
    }
</script>

<p>{$t("introduction.tool.generate")}</p>

<p>{$t("instruction.tool.generate")}</p>

<form>
    <input bind:value>
    <button type="submit" on:click={do_query}>[l6e] Generate</button>
    <button on:click|preventDefault={() => value = ""}>[l6e] Reset</button>
</form>
