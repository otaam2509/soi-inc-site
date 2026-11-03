const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const code = fs.readFileSync('assets/js/measurement.js', 'utf8');
const events = [];
let onClick;
const page = new URL('https://soi-co-ltd.com/tsuimiru/?private_query=excluded');
const scope = {URL, location: page, window: {gtag: (...args) => events.push(args)},
  document: {addEventListener: (name, handler) => { assert.equal(name, 'click'); onClick = handler; }}};
vm.runInNewContext(code, scope);
function click(href, track, service) {
  const attrs = {'data-track': track, 'data-contact-service': service};
  const link = {href, hasAttribute: name => Boolean(attrs[name]), getAttribute: name => attrs[name]};
  onClick({target: {closest: () => link}});
}
click('https://ig.me/m/tsuimiru_aimovie');
click('https://lin.ee/TMkuCTn');
click('mailto:example@example.com?body=private-message');
click('https://www.instagram.com/tsuimiru_aimovie/', 'instagram_profile');
assert.deepEqual(events.map(e => [e[1],e[2].method]), [
  ['contact_click','instagram_dm'],['contact_click','line'],['contact_click','mail'],['contact_click','instagram_profile']]);
assert.ok(events.every(e => e[2].page_path === '/tsuimiru/'));
click('/column/short-drama-production-company/?query=private-message');
click('/recruit/video/');
assert.deepEqual(events.slice(4).map(e => [e[1],e[2].content_type,e[2].item_id]), [
  ['select_content','article','/column/short-drama-production-company/'],['select_content','service','/recruit/video/']]);
click('#contact');
click('https://example.com/recruit/');
click('https://ig.me/m/another-account');
assert.equal(events.length, 6);
click('https://lin.ee/TMkuCTn', 'line', 'recruit');
click('https://lin.ee/SC6LK06', 'line', 'tsuimiru');
click('https://lin.ee/SC6LK06', 'line', 'private-service-value');
assert.deepEqual(events.slice(6).map(e => e[2].service), ['recruit', 'tsuimiru', undefined]);
assert.equal(events.length, 9);
onClick({target: {closest: () => null}});
scope.window.gtag = undefined;
click('https://ig.me/m/tsuimiru_aimovie');
assert.equal(events.length, 9);
assert.ok(!JSON.stringify(events).includes('private'));
assert.ok(!JSON.stringify(events).includes('example@example.com'));
assert.ok(!JSON.stringify(events).includes('generate_lead'));
console.log('PASS: contact methods, service attribution whitelist, internal routes, no private data, safe without analytics');
