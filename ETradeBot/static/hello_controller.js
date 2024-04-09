import { Application, Controller } from "https://cdn.skypack.dev/stimulus";

const application = Application.start();

export class HelloController extends Controller {
  static targets = ["name", "output"];

  greet() {
    this.outputTarget.textContent = `Hello, ${this.nameTarget.value}!`;
  }
}

application.register("hello", HelloController);
