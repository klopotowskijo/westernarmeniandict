import AppKit
import Foundation
import Vision

struct OCRResult: Encodable {
    let path: String
    let text: String
}

func usage() -> Never {
    let message = "usage: swift ocr_images_with_vision.swift [--json] [--languages hy,en] <image-path> [<image-path> ...]\n"
    fputs(message, stderr)
    exit(1)
}

func parseArguments() -> (json: Bool, languages: [String], paths: [String]) {
    var json = false
    var languages: [String] = []
    var paths: [String] = []
    var index = 1
    let args = CommandLine.arguments

    while index < args.count {
        let arg = args[index]
        if arg == "--json" {
            json = true
            index += 1
            continue
        }
        if arg == "--languages" {
            guard index + 1 < args.count else {
                usage()
            }
            languages = args[index + 1]
                .split(separator: ",")
                .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
                .filter { !$0.isEmpty }
            index += 2
            continue
        }
        paths.append(arg)
        index += 1
    }

    if paths.isEmpty {
        usage()
    }
    return (json, languages, paths)
}

func loadCGImage(from path: String) -> CGImage? {
    guard let image = NSImage(contentsOfFile: path) else {
        return nil
    }
    guard let tiffData = image.tiffRepresentation,
          let bitmap = NSBitmapImageRep(data: tiffData),
          let cgImage = bitmap.cgImage else {
        return nil
    }
    return cgImage
}

func recognizeText(path: String, languages: [String]) throws -> OCRResult {
    guard let cgImage = loadCGImage(from: path) else {
        throw NSError(domain: "VisionOCR", code: 2, userInfo: [NSLocalizedDescriptionKey: "Failed to decode image at \(path)"])
    }

    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = false
    if !languages.isEmpty {
        request.recognitionLanguages = languages
    }

    let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
    try handler.perform([request])
    let text = (request.results ?? []).compactMap { observation in
        observation.topCandidates(1).first?.string
    }.joined(separator: "\n")
    return OCRResult(path: path, text: text)
}

let options = parseArguments()
var results: [OCRResult] = []

do {
    for path in options.paths {
        results.append(try recognizeText(path: path, languages: options.languages))
    }

    if options.json {
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .withoutEscapingSlashes]
        let data = try encoder.encode(results)
        FileHandle.standardOutput.write(data)
        FileHandle.standardOutput.write(Data("\n".utf8))
    } else {
        for result in results {
            print("=== \(result.path) ===")
            print(result.text)
        }
    }
} catch {
    fputs("OCR failed: \(error.localizedDescription)\n", stderr)
    exit(2)
}