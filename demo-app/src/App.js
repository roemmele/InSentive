import React, { useState } from "react";
import axios from "axios";
import "./App.css";
import "./milligram.css";
import Loader from "react-loader-spinner";

function Interaction() {
    const [isGenerating, setIsGenerating] = useState(false);
    const [modelType, setModelType] = useState("generic");
    const [output, setOutput] = useState([]);

    const handleKeyDown = (event) => {
        if (event.key === "Enter") {
            setIsGenerating(true);
            return getExpansions(event.target.value);
        }
    };
    const getExpansions = (input) => {
        console.log(modelType);
        axios
            .post("/expand", {
                input: input,
                model_type: modelType,
            })
            .then((response) => {
                let curOutput = response.data["output"];
                console.log(curOutput);
                if (curOutput.length == 0) {
                    curOutput.push({
                        text: "No expansions found",
                        input_token_idxs: null,
                    });
                }
                setOutput(curOutput);
                setIsGenerating(false);
            });
    };

    const formattedOutput = output.map((item, idx) => {
        const text = item["text"];
        const input_token_idxs = item["input_token_idxs"];
        if (input_token_idxs == null) {
            return (
                <p key={0}>
                    <span>{text}</span>
                </p>
            );
        }
        var displayText = [];
        var last_end_token_idx = 0;
        for (var i = 0; i < input_token_idxs.length; i++) {
            const start_token_idx = input_token_idxs[i][0];
            displayText.push(
                <span>{text.slice(last_end_token_idx, start_token_idx)}</span>
            );
            var end_token_idx = input_token_idxs[i][1];
            displayText.push(
                <span>
                    <b>{text.slice(start_token_idx, end_token_idx)}</b>
                </span>
            );
            if (i == input_token_idxs.length - 1) {
                displayText.push(<span>{text.slice(end_token_idx)}</span>);
            }
            last_end_token_idx = end_token_idx;
        }
        return <p key={idx}>{displayText}</p>;
    });

    // const handleChangeModelType = (event) => {
    //     setModelType(event.target.value);
    // };

    return (
        <div>
            {/*           <label class="box-label" style={{fontSize:"1rem", paddingBottom:"0px"}}>Model Type</label>
            <select id="modelType" style={{maxWidth:"15%"}} onChange={handleChangeModelType} value={modelType}>
              <option value="bookcorpus">BookCorpus</option>
            </select>*/}
            {/*            <label
                class="box-label"
                style={{
                    fontSize: "1rem",
                }}
            >
                Input
            </label>*/}
            <textarea
                placeholder="Enter words here and hit enter to expand"
                onKeyDown={handleKeyDown}
                disabled={isGenerating}
            ></textarea>
            <Loader
                type="ThreeDots"
                color="#9b4dca"
                height={20}
                width={20}
                visible={isGenerating}
            />
            {!isGenerating ? formattedOutput : ""}
        </div>
    );
}

function App() {
    return (
        <div className="container">
            <br />
            <h2 id="title">Sentence Infilling</h2>
            <br />
            <Interaction />
        </div>
    );
}

export default App;
