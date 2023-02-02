export function only_on_enter(fn) {
    return function (ev) {
        if (ev.key !== "Enter") return;
        fn();
    }
}


// https://blog.webdevsimplified.com/2020-07/relative-time-format/
const DIVISIONS = [
    { amount: 60, name: 'seconds' },
    { amount: 60, name: 'minutes' },
    { amount: 24, name: 'hours' },
    { amount: 7, name: 'days' },
    { amount: 4.34524, name: 'weeks' },
    { amount: 12, name: 'months' },
    { amount: Number.POSITIVE_INFINITY, name: 'years' },
];

const RELTIME_FMT_OPTS = { };
export function fmt_date_ago_localized(date, locale) {
    if (!date) return null;
    let diff_sec = (date - Date.now()) / 1000;

    const formatter = new Intl.RelativeTimeFormat(locale, RELTIME_FMT_OPTS);
    for (let i = 0; i <= DIVISIONS.length; i++) {
        const division = DIVISIONS[i]
        if (Math.abs(diff_sec) < division.amount) {
            return formatter.format(Math.round(diff_sec), division.name)
        }
        diff_sec /= division.amount
    }

    // the loop with the if check should always hit, so we return early.
    // if that doesn't happen, something is very wrong
    throw new Error("unreachable?");
}
