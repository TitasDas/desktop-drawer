const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
let batches = [], closed = 0, reads = 0;
const notifications = [];
const info = (name, type = 1, hidden = false) => ({get_name: () => name, get_display_name: () => name,
    get_file_type: () => type, get_is_hidden: () => hidden});
const enumerator = {
    next_files_async(n, p, c, cb) { reads++; cb(this, batches.shift() || []); },
    next_files_finish(result) { if (result instanceof Error) throw result; return result; },
    close_async(p, c, cb) { assert.equal(c, null); closed++; cb(this, true); },
    close_finish() {}
};
const Gio = {FileType: {DIRECTORY: 2}, FileQueryInfoFlags: {NOFOLLOW_SYMLINKS: 1}, File: {
    new_for_path: p => ({
        enumerate_children_async(q, flags, priority, token, cb) {
            assert.equal(flags, 1); cb(this, true);
        }, enumerate_children_finish: () => enumerator,
        get_basename: () => path.basename(p), get_uri: () => 'file://' + p
    })
}};
class Item {
    constructor(label) { this.label = label; this.actor = {connect() {}}; this.menu = {
        connect(event, cb) { this.openCallback = cb; }
    }; }
    destroy() { this.destroyed = true; }
}
const context = vm.createContext({imports: {ui: {
    applet: {IconApplet: class {}}, popupMenu: {PopupMenuItem: Item, PopupSubMenuMenuItem: Item}, settings: {}, main: {notifyError: (...args) => notifications.push(args)}
}, gi: {Gio, GLib: {PRIORITY_DEFAULT: 0, get_home_dir: () => '/home/demo', build_filenamev: x => x.join('/'), path_is_absolute: path.isAbsolute}, St: {}},
mainloop: {}, gettext: {bindtextdomain() {}, dgettext: (d,t) => t}}});
vm.runInContext(fs.readFileSync(path.join(__dirname, '../desktop/applet/desktop-drawer@linux-automations/applet.js'), 'utf8') + '\nglobalThis.Drawer = DesktopDrawerApplet;', context);
const drawer = Object.create(context.Drawer.prototype);
(async () => {
    assert.equal(drawer._shortLabel('📁'.repeat(30)), '📁'.repeat(30), 'short Unicode names stay intact');
    assert.equal(drawer._shortLabel('📁'.repeat(50)), '📁'.repeat(20) + '...' + '📁'.repeat(20));
    drawer.folder = '/demo/folder with trailing space ';
    assert.equal(await drawer._rootPath({}), drawer.folder);
    drawer.folder = 'relative';
    await assert.rejects(drawer._rootPath({}), /absolute/);
    batches = [[info('.hidden',1,true), info('z.txt'), info('Folder',2), info('link',3)]];
    let result = await drawer._readDirectory('/demo', {});
    assert.equal(result.entries[0].name, 'Folder');
    assert.equal(result.entries.length, 3);
    assert.equal(result.entries.find(e => e.name === 'link').isDirectory, false);
    assert.equal(result.truncated, false);
    assert.equal(closed, 1);
    batches = [Array.from({length:30}, (_,i) => info('file'+i)), [info('extra')]];
    result = await drawer._readDirectory('/demo', {});
    assert.equal(result.entries.length, 30); assert.equal(result.truncated, true);
    batches = Array.from({length:12}, () => Array.from({length:30}, () => info('.hidden',1,true)));
    reads = 0; result = await drawer._readDirectory('/demo', {});
    assert.equal(reads,10); assert.equal(result.truncated,true);
    batches = [new Error('read cancelled')];
    await assert.rejects(drawer._readDirectory('/demo', {}), /cancelled/);
    assert.equal(closed,4);

    const menu = {items:[], addMenuItem(i) { this.items.push(i); }};
    let displayed = [];
    drawer._generation = 1; drawer._removed = false;
    drawer._readDirectory = async () => ({entries:[{name:'pRiVaTe',path:'/demo/Private',isDirectory:true},
        {name:'Private',label:'Private',path:'/demo/Private-file',isDirectory:false},
        {name:'regular.txt',label:'regular.txt',path:'/demo/regular.txt',isDirectory:false}],truncated:false});
    drawer._addOpenItem = (m,p,l,icon) => displayed.push([p,l,icon || 'folder-open-symbolic']);
    await drawer._populate(menu,'/demo',2,1,{});
    assert.deepEqual(displayed,[
        ['/demo/Private','Open Private folder','folder-open-symbolic'],
        ['/demo/Private-file','Private','text-x-generic-symbolic'],
        ['/demo/regular.txt','regular.txt','text-x-generic-symbolic']
    ], 'only directories named Private should use the private-folder action');
    displayed=[];
    await drawer._populate(menu,'/demo',0,0,{});
    assert.equal(displayed.length,0, 'stale reads must not populate a replaced menu');
    drawer._removed=true;
    await drawer._populate(menu,'/demo',0,1,{});
    assert.equal(displayed.length,0, 'removed applets must not update menus');
    drawer._removed=false;
    drawer._readDirectory = async () => {throw new Error('permission denied');};
    await drawer._populate(menu,'/demo',0,1,{});
    assert.match(menu.items.at(-1).label,/Cannot read/);

    let populations=0;
    drawer._populate = () => populations++;
    drawer._addDirectoryMenu(menu,{label:'Folder',path:'/demo/folder'},0,1,{});
    const sub=menu.items.at(-1).menu;
    assert.equal(populations,0,'subfolders must load lazily');
    sub.openCallback(sub,true); sub.openCallback(sub,true);
    assert.equal(populations,1,'load each submenu only once per drawer opening');
    drawer._addDirectoryMenu(menu,{label:'Deep',path:'/demo/deep'},2,1,{});
    menu.items.at(-1).menu.openCallback(menu.items.at(-1).menu,true);
    assert.equal(populations,1,'depth limit must prevent further enumeration');
    drawer.menu = {close() {}};
    context.global = {create_app_launch_context() {return {};}};
    Gio.AppInfo = {
        launch_default_for_uri_async(uri, context, cancel, callback) { callback(null, true); },
        launch_default_for_uri_finish() {throw new Error('no handler');}
    };
    drawer._openPath('/demo/missing');
    assert.equal(notifications.length, 1, 'launch failures must have visible feedback');
    assert.equal(notifications[0][0], 'Could not open this item');
    drawer._removed = true;
    drawer._openPath('/demo/missing');
    assert.equal(notifications.length, 1, 'do not notify after applet removal');
    console.log('PASS: filtering, symlinks, scan bounds, cancellation cleanup, nested Private, stale reads, errors, lazy submenus and depth limit');
})().catch(e=>{console.error(e);process.exitCode=1;});
