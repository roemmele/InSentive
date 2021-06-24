import React, { useState } from "react";
import logo from "./logo.svg";
import axios from "axios";
import Loader from "react-loader-spinner";
import "./App.css";
import "./milligram.css";
import { instructionsText } from "./instructions";

function App() {
    const nUserSentsPerItem = 2;
    const showGeneratedStories = true;

    const [state, setState] = useState({
        started: false,
        finished: false,
        nInputItems: null,
        sessionID: null,
        showUserInputForm: false,
        waitingForUserInput: false,
        userSentenceData: {
            sentences: Array(nUserSentsPerItem).fill(""),
            areValid: Array(nUserSentsPerItem).fill(null),
            msgs: Array(nUserSentsPerItem).fill(null),
            highlightCharIdxs: Array(nUserSentsPerItem).fill(null),
            stories: Array(nUserSentsPerItem).fill(null),
        },
        curInputItem: {
            inputNum: null,
            inputWords: null,
            genSentenceData: {
                sentences: null,
                highlightCharIdxs: null,
                showSentences: null,
            },
        },
    });

    const highlightSentDisplay = (sent, charIdxs) => {
        let sentDisplay = [];
        let prevEndIdx = 0;
        let keyID = 0;
        charIdxs.forEach((startEndIdxs, iterIdx) => {
            const [startIdx, endIdx] = startEndIdxs;
            sentDisplay.push(
                <span key={keyID}>{sent.slice(prevEndIdx, startIdx)}</span>
            );
            keyID += 1;
            sentDisplay.push(
                <span key={keyID} className="emphatic-text">
                    {sent.slice(startIdx, endIdx)}
                </span>
            );
            keyID += 1;
            if (iterIdx == charIdxs.length - 1) {
                sentDisplay.push(<span key={keyID}>{sent.slice(endIdx)}</span>);
            }
            prevEndIdx = endIdx;
        });
        return sentDisplay;
    };

    const getNextInput = () => {
        console.log("get next inputs");
        axios.get("/retrieve_item").then((response) => {
            const inputItem = response.data;
            if (Object.keys(inputItem).length == 0) {
                setState((curState) => ({
                    ...curState,
                    finished: true,
                }));
            } else {
                setState((curState) => ({
                    ...curState,
                    // userInputMode: true,
                    curInputItem: {
                        inputNum: inputItem["item_num"],
                        inputWords: inputItem["input_tokens"],
                        genSentenceData: {
                            sentences: inputItem["gen_sents"],
                            highlightCharIdxs:
                                inputItem["input_token_char_idxs"],
                            showSentences: inputItem["show_gen_sents"],
                        },
                    },
                }));
            }
        });
    };

    const handleUserSentenceChange = (sentenceIdx, event) => {
        let curUserSentences = [...state.userSentenceData.sentences];
        curUserSentences[sentenceIdx] = event.target.value;
        setState((curState) => ({
            ...curState,
            userSentenceData: {
                ...curState.userSentenceData,
                sentences: curUserSentences,
            },
        }));
    };

    const handleItemSubmit = () => {
        setState((curState) => ({
            ...curState,
            waitingForUserInput: false,
        }));
        const userResponse = {
            userSentences: state.userSentenceData.sentences,
        };
        axios.post("/submit_item", userResponse).then((response) => {
            const statuses = response.data["statuses"];
            const highlightCharIdxs = response.data["input_token_char_idxs"];
            let areValid = [];
            let msgs = [];
            statuses.forEach(function (status) {
                const isValid = status["is_valid"];
                const msg = status["error_msg"];
                areValid.push(isValid);
                msgs.push(msg);
            });
            setState((curState) => ({
                ...curState,
                userSentenceData: {
                    ...curState.userSentenceData,
                    areValid: areValid,
                    msgs: msgs,
                },
            }));
            const allAreValid = areValid.every((isValid) => {
                return isValid;
            });
            if (allAreValid) {
                setState((curState) => ({
                    ...curState,
                    userSentenceData: {
                        ...curState.userSentenceData,
                        highlightCharIdxs: highlightCharIdxs,
                    },
                }));
                handleSubmitSuccess();
            } else {
                console.log("valid");
                setState((curState) => ({
                    ...curState,
                    waitingForUserInput: true,
                }));
            }
        });
    };

    const handleSubmitSuccess = () => {
        if (showGeneratedStories) {
            const userResponse = {
                userSentences: state.userSentenceData.sentences,
            };
            console.log(state.waitingForUserInput);
            // setState((curState) => ({
            //         ...curState,
            //     }));
            axios.post("/generate_stories", userResponse).then((response) => {
                const genStories = response.data["generated_stories"];
                setState((curState) => ({
                    ...curState,
                    userSentenceData: {
                        ...curState.userSentenceData,
                        stories: genStories,
                    },
                    showUserInputForm: false,
                }));
            });
        } else {
            clearUserResponse();
            getNextInput();
        }
    };

    const clearUserResponse = () => {
        setState((curState) => ({
            ...curState,
            userSentenceData: {
                sentences: Array(nUserSentsPerItem).fill(""),
                areValid: Array(nUserSentsPerItem).fill(null),
                msgs: Array(nUserSentsPerItem).fill(null),
                highlightCharIdxs: Array(nUserSentsPerItem).fill(null),
                stories: Array(nUserSentsPerItem).fill(null),
            },
        }));
    };

    const handleEvalStart = () => {
        axios.get("/index").then((response) => {
            setState((curState) => ({
                ...curState,
                started: true,
                nInputItems: response.data["n_input_items"],
                sessionID: response.data["session_id"],
                showUserInputForm: true,
                waitingForUserInput: true,
            }));
            // console.log(state);
            getNextInput();
        });
    };

    const sentenceBoxes = () => {
        let boxes = [];
        for (let i = 0; i < nUserSentsPerItem; i++) {
            const sentIdx = i;
            boxes.push(
                <div key={sentIdx} className="sentence-box">
                    <b className="sentence-label">
                        {"Sentence " + (sentIdx + 1)}
                    </b>
                    <textarea
                        className="sentence-box-textarea"
                        type="text"
                        value={state.userSentenceData.sentences[sentIdx]}
                        onChange={(event) => {
                            handleUserSentenceChange(sentIdx, event);
                        }}
                        disabled={!state.waitingForUserInput}
                    />
                    <span className="error-text">
                        {!(state.userSentenceData.areValid[sentIdx] == null)
                            ? state.userSentenceData.msgs[sentIdx]
                            : null}
                    </span>
                </div>
            );
        }
        return boxes;
    };

    const storyDisplay = () => {
        //console.log(state);
        let displayedStories = [];
        const sents = state.userSentenceData.sentences;
        const highlightCharIdxs = state.userSentenceData.highlightCharIdxs;
        const stories = state.userSentenceData.stories;
        for (let sentIdx = 0; sentIdx < sents.length; sentIdx++) {
            const sent = sents[sentIdx];
            const story = stories[sentIdx];
            const charIdxs = highlightCharIdxs[sentIdx];
            const highlightedSent = highlightSentDisplay(sent, charIdxs);

            displayedStories.push(
                <div key={sentIdx + 1}>
                    <span className="sentence-label">
                        {"Sentence " + (sentIdx + 1) + " Story"}
                        <br />
                    </span>
                    <p className="example-sentence story">{highlightedSent}<span>{story}</span></p>
                </div>
            );
        }
        return <div>{displayedStories}</div>;
    };

    const genSentsDisplay = () => {
        let displayedLabel = (
            <span className="examples-label">{"Examples:"}</span>
        );
        let displayedSents = [];
        const sents = state.curInputItem.genSentenceData.sentences;
        const highlightCharIdxs =
            state.curInputItem.genSentenceData.highlightCharIdxs;
        for (let sentIdx = 0; sentIdx < sents.length; sentIdx++) {
            const sent = sents[sentIdx];
            const charIdxs = highlightCharIdxs[sentIdx];
            const displayedSent = highlightSentDisplay(sent, charIdxs);

            displayedSents.push(
                <span key={sentIdx + 1} className="example-sentence">
                    <small>
                        {displayedSent}
                        <br />
                    </small>
                </span>
            );
        }
        return (
            <div>
                {displayedLabel}
                <div className="sents-group">{displayedSents}</div>
            </div>
        );
    };

    const userInputForm = () => {
        const onSubmit = (event) => {
            event.preventDefault();
            handleItemSubmit();
        };

        return (
            <div>
                <h5 className="input-string">
                    <span>{"Write two sentences with these words: "}</span>
                    <span className="emphatic-text">
                        {state.curInputItem.inputWords
                            ? state.curInputItem.inputWords.join(", ")
                            : null}
                    </span>
                </h5>
                <div>
                    {state.curInputItem.genSentenceData.showSentences == true &&
                    state.curInputItem.genSentenceData.sentences != null
                        ? genSentsDisplay()
                        : null}
                </div>
                <form id="userInputForm" onSubmit={onSubmit}>
                    <fieldset>
                        <div className="sentence-box-group">
                            {sentenceBoxes()}
                        </div>
                        <br />
                        <input
                            className="proceed-button"
                            type="submit"
                            value="Submit"
                            disabled={!state.waitingForUserInput}
                        />
                        <Loader
                            type="TailSpin"
                            color="#9b4dca"
                            height={25}
                            width={25}
                            visible={!state.waitingForUserInput}
                            style={{
                                display: "inline-block",
                                marginLeft: "15px",
                            }}
                        />
                    </fieldset>
                </form>
            </div>
        );
    };

    const storyDisplayForm = () => {
        const onContinue = (event) => {
            event.preventDefault();
            clearUserResponse();
            getNextInput();
            setState((curState) => ({
                ...curState,
                showUserInputForm: true,
                waitingForUserInput: true,
            }));
        };
        console.log("story display");
        return (
            <div>
                <h5>
                    <span>
                        {"Stories for your sentences with these words: "}
                    </span>
                    <span className="emphatic-text">
                        {state.curInputItem.inputWords
                            ? state.curInputItem.inputWords.join(", ")
                            : null}
                    </span>
                </h5>
                <form id="storyDisplayForm" onSubmit={onContinue}>
                    <fieldset>
                        {storyDisplay()}
                        <br />
                        <input
                            type="submit"
                            className="proceed-button"
                            value="Continue"
                        />
                    </fieldset>
                </form>
            </div>
        );
    };

    const evalPage = () => {
        return (
            <div>
                <h3 className="title item-title">
                    {"Item " +
                        state.curInputItem.inputNum +
                        " / " +
                        state.nInputItems}
                </h3>
                <p className="error-text">
                    Do not refresh the page or navigate to the previous page
                </p>
                {state.showUserInputForm || !showGeneratedStories
                    ? userInputForm()
                    : storyDisplayForm()}
            </div>
        );
    };

    const endPage = () => {
        return (
            <div>
                <h3>
                    You have completed all items, thank you! If participating
                    via Amazon Mechanical Turk, please use this code for
                    verification:
                    <b> {state.sessionID}</b>
                </h3>
            </div>
        );
    };

    const introPage = () => {
        return (
            <div>
                <h2 className="title">SentCraft</h2>
                {instructionsText}
                <input
                    // type="button"
                    className="proceed-button"
                    type="submit"
                    value="Start"
                    onClick={handleEvalStart}
                />
            </div>
        );
    };

    // console.log(state);

    return (
        <section id="page" className="container">
            {state.started
                ? state.finished
                    ? endPage()
                    : evalPage()
                : introPage()}
        </section>
    );
}

export default App;
