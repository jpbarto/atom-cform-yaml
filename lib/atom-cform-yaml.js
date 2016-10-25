'use babel';

import AtomCformYamlView from './atom-cform-yaml-view';
import { CompositeDisposable } from 'atom';

export default {

  atomCformYamlView: null,
  modalPanel: null,
  subscriptions: null,

  config: {
    verbose: {
      type: 'boolean',
      default: false
    }
  },

  activate(state) {
    this.atomCformYamlView = new AtomCformYamlView(state.atomCformYamlViewState);
    this.modalPanel = atom.workspace.addModalPanel({
      item: this.atomCformYamlView.getElement(),
      visible: false
    });

    // Events subscribed to in atom's system can be easily cleaned up with a CompositeDisposable
    this.subscriptions = new CompositeDisposable();

    // Register command that toggles this view
    this.subscriptions.add(atom.commands.add('atom-workspace', {
      'atom-cform-yaml:toggle': () => this.toggle()
    }));
  },

  deactivate() {
    this.modalPanel.destroy();
    this.subscriptions.dispose();
    this.atomCformYamlView.destroy();
  },

  serialize() {
    return {
      atomCformYamlViewState: this.atomCformYamlView.serialize()
    };
  },

  toggle() {
    console.log('AWS CloudFormation (YAML) was toggled!');
    return (
      this.modalPanel.isVisible() ?
      this.modalPanel.hide() :
      this.modalPanel.show()
    );
  }

};
