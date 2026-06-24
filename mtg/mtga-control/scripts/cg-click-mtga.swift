import AppKit
import CoreGraphics
import Foundation

let usage = """
Usage:
  swift cg-click-mtga.swift --relative <x> <y>
  swift cg-click-mtga.swift --absolute <x> <y>

Coordinates for --relative are window-relative screenshot coordinates from computer-use.
"""

func fail(_ message: String) -> Never {
    fputs("error: \(message)\n\(usage)\n", stderr)
    exit(1)
}

let args = CommandLine.arguments.dropFirst()
guard args.count == 3 else {
    fail("expected a mode and two coordinates")
}

let mode = args[args.startIndex]
let xArg = args[args.index(after: args.startIndex)]
let yArg = args[args.index(args.startIndex, offsetBy: 2)]

guard let inputX = Double(xArg), let inputY = Double(yArg) else {
    fail("coordinates must be numbers")
}

func mtgaWindowBounds() -> CGRect? {
    guard let windows = CGWindowListCopyWindowInfo([.optionOnScreenOnly], kCGNullWindowID) as? [[String: Any]] else {
        return nil
    }

    for window in windows {
        let ownerName = window[kCGWindowOwnerName as String] as? String
        let windowName = window[kCGWindowName as String] as? String
        guard ownerName == "MTGA" || windowName == "MTGA" else {
            continue
        }
        guard let boundsDict = window[kCGWindowBounds as String] as? [String: Any],
              let x = boundsDict["X"] as? Double,
              let y = boundsDict["Y"] as? Double,
              let width = boundsDict["Width"] as? Double,
              let height = boundsDict["Height"] as? Double,
              width > 0,
              height > 0 else {
            continue
        }
        return CGRect(x: x, y: y, width: width, height: height)
    }

    return nil
}

let point: CGPoint
switch mode {
case "--absolute":
    point = CGPoint(x: inputX, y: inputY)
case "--relative":
    guard let bounds = mtgaWindowBounds() else {
        fail("could not find a visible MTGA window")
    }
    point = CGPoint(x: bounds.minX + inputX, y: bounds.minY + inputY)
default:
    fail("unknown mode \(mode)")
}

if let app = NSRunningApplication.runningApplications(withBundleIdentifier: "com.wizards.mtga").first {
    app.activate(options: [.activateAllWindows])
    usleep(150_000)
}

guard let source = CGEventSource(stateID: .hidSystemState),
      let down = CGEvent(mouseEventSource: source, mouseType: .leftMouseDown, mouseCursorPosition: point, mouseButton: .left),
      let up = CGEvent(mouseEventSource: source, mouseType: .leftMouseUp, mouseCursorPosition: point, mouseButton: .left) else {
    fail("could not create mouse events")
}

down.post(tap: .cghidEventTap)
usleep(90_000)
up.post(tap: .cghidEventTap)
usleep(250_000)

print("clicked MTGA at \(Int(point.x)),\(Int(point.y))")
