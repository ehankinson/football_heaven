use rand::Rng;
use serde_json::json;
use std::collections::HashMap;
use std::fs::File;
use std::io::Write;
use indicatif::{ProgressBar, ProgressStyle};

fn main() {
    let sim: u64 = 10_000_000;
    let mut result: HashMap<u64, HashMap<String, f64>> = HashMap::new();

    // Create a progress bar for the simulation
    let pb = ProgressBar::new(sim);
    pb.set_style(ProgressStyle::default_bar()
        .template("{msg} {bar:40} {pos}/{len} ({percent}%)")
        .progress_chars("##-"));

    // Simulation loop
    for _ in 0..sim {
        let mut made = 1;
        let mut shots = 2;

        for i in 2..101 {
            let probability = made as f64 / shots as f64;
            if rand::thread_rng().gen::<f64>() < probability {
                made += 1;
            }
            shots += 1;
        }

        // Update the result map
        let entry = result.entry(made).or_insert_with(|| {
            let mut map = HashMap::new();
            map.insert("amount".to_string(), 0.0);
            map.insert("pct".to_string(), 0.0);
            map
        });
        entry.insert("amount".to_string(), entry["amount"] + 1.0);

        // Update the progress bar
        pb.inc(1);
    }

    pb.finish_with_message("Simulation complete!");

    // Write results to JSON file
    let mut output = HashMap::new();
    for (key, value) in &result {
        output.insert(key, value);
    }

    let json_output = serde_json::to_string_pretty(&output).unwrap();
    let mut file = File::create("stats.json").unwrap();
    file.write_all(json_output.as_bytes()).unwrap();

    // Calculate percentages and print results
    let mut keys: Vec<u64> = result.keys().cloned().collect();
    keys.sort();

    for key in keys {
        let amount = result[&key]["amount"];
        let pct = (amount / sim as f64) * 100.0;
        println!("The odds of making {} shots is {:.2}%", key, pct);
    }
}