export function only_on_enter(fn) {
    return function (ev) {
        if (ev.key !== "Enter") return;
        fn();
    }
}

export function *enumerate(list, start = 0) {
    for (let i = start; i < list.length; i++) {
        yield [i, list[i]];
    }
}

export function boundcheck(x, y, limit_x, limit_y, function_name) {
    let err = [];
    if (y >= limit_y) {
        err.push(`y=${y} is too large (max y coord is ${this.#y - 1})`);
    } else if (y < 0) {
        err.push(`y=${y} is too small (min y coord is 0)`);
    }
    if (x >= limit_x) {
        err.push(`x=${x} is too large (max x coord is ${this.#x - 1})`);
    } else if (x < 0) {
        err.push(`x=${x} is too small (min x coord is 0)`);
    }
    if (err.length > 0) {
        throw new Error(`${funcname}(y, x): out of bounds: ` + err.join(", "));
    }
}

export function trim(str, trim_characters = " \t\n") {
    if (typeof str !== "string") {
        throw new TypeError("trim(): argument must be string");
    }
    trim_characters = new Set(trim_characters);

    let start = -1;
    let end = str.length;

    while (trim_characters.has(str[++start])) ;
    while (trim_characters.has(str[--end])) ;

    return str.slice(start, end + 1);
}

// pad out the string `str` to length `size`,
// padding by spaces on each side
export function pad_center(str, size) {
    if (str.length >= size) {
        return str;
    }

    let pad_left, pad_right;
    if (size % 2 === 0) {
        pad_left = pad_right = size / 2;
    } else {
        pad_left = size / 2 - 1;
        pad_right = size / 2;
    }

    pad_left = " ".repeat(pad_left);
    pad_right = " ".repeat(pad_right);
    return pad_left + str + pad_right;
}

/*
    deep_len(arr)
    total length of array `arr`, including length of subarrays, e.g.
    tot_len([1, 2, 3]) == 3,
    tot_len([1, 2, [3, 4]]) == 4
*/
export const deep_len = arr => !Array.isArray(arr) ? 1 : arr.map(deep_len).reduce((prev, cur) => prev + cur);
export const is_pojo = obj => !!obj && obj.constructor === Object;

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
