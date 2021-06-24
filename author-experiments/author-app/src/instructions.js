import React from "react";
import "./App.css";
import "./milligram.css";

export const instructionsText = (
    <div>
        <p className="instructions-paragraph">
            In this task, each item will show you a list of words. You will
            write different sentences that contain those words. The sentences
            can be about anything. Try to write sentences that evoke a story
            someone would be curious to hear more about. Here are some examples:
        </p>

        <p id="instructions-examples">
            <b>Words: the, bark, tree</b>
            <br />
            <span className="computer-text">
                <i>Sentence 1:</i> <b className="emphatic-text">The</b> dog gave
                a <b className="emphatic-text">bark</b> of warning at the
                oblivious cat lounging in the{" "}
                <b className="emphatic-text">tree</b>.<br />
                <i>Sentence 2:</i> I carved her name into{" "}
                <b className="emphatic-text">the bark</b> of the{" "}
                <b className="emphatic-text">tree</b>.<br />
                {/*<i>Sentence 3:</i> Even <b className="emphatic-text">the</b>{" "}
                best detectives may occasionally{" "}
                <b className="emphatic-text">bark</b> up the wrong{" "}
                <b className="emphatic-text">tree</b> and overlook important
                clues.
                <br />*/}
            </span>
            <br />
            <b>Words: bank, plan, work</b> <br />
            <span className="computer-text">
                <i>Sentence 1:</i> After the robbery, some of the{" "}
                <b className="emphatic-text">bank</b> employees did not{" "}
                <b className="emphatic-text">plan</b> to return to{" "}
                <b className="emphatic-text">work</b> for awhile.
                <br />
                <i>Sentence 2:</i> Ella thought she could{" "}
                <b className="emphatic-text">bank</b> on the success of her{" "}
                <b className="emphatic-text">plan</b>, but ultimately it didn't{" "}
                <b className="emphatic-text">work</b>.<br />
                {/*<i>Sentence 3:</i> Our office north of the river{" "}
                    <b className="emphatic-text">bank</b> had an open floor{" "}
                    <b className="emphatic-text">plan</b> that made it easy for
                    us to <b className="emphatic-text">work</b> together.*/}
            </span>
        </p>
        <p className="instructions-paragraph">
            You will see the same word prompts repeated twice at different times
            during the task. The second time you see a particular item, you will
            also see example sentences that use the words. You can use these
            examples to get ideas, but your sentences must be different from the
            examples.
        </p>

        <p className="instructions-paragraph">
            <b>
                Additionally, the sentences must meet these criteria:
                <br />
            </b>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{"\u2022"}{" "}
            <b>
                Each sentence must contain all words given in the prompt list,
                and words must appear in the same order as they are shown in the
                list.{" "}
            </b>
            It is fine to capitalize the prompt words in the sentence.
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{"\u2022"}{" "}
            <b>
                Each sentence must contain at least 7 words but no more than 50
                words.
                <br />
            </b>
            You will be alerted to modify sentences that don't meet these
            requirements when submitting them.
        </p>

        <p className="instructions-paragraph">
            There are no "correct" sentences in this task. Do your best to write
            a full sentence containing all words, using whatever ideas come to
            mind. Once you submit your sentences, you will be shown some story
            excerpts that incorporate your sentences. The more playful you are
            with your sentences, the more entertaining the excerpts will be.
        </p>
        <p className="instructions-paragraph">
            Some of the content shown to you may be deemed PG-13. There is a
            small risk of explicit and/or offensive content.
        </p>
        <p className="instructions-paragraph">
            Do not hit the back or refresh button while you are completing this
            task, otherwise you will be sent back to this start page.
        </p>
    </div>
);
