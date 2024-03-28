import fs from "fs";
import path from "path";

import { BASE_URL } from "../constants/index.js";

export const getMatchIdList = async (browser, country, league) => {
  const page = await browser.newPage();

  const url = `${BASE_URL}/football/${country}/${league}/results/`;
  await page.goto(url);

  while (true) {
    try {
      await page.evaluate(async _ => {
        await new Promise(resolve => setTimeout(resolve, 1500));
        const element = document.querySelector('a.event__more.event__more--static');
        element.scrollIntoView();
        element.click();
      });
    } catch (error) {
      break;
    }
  }

  const matchIdList = await page.evaluate(_ => {
    return Array.from(document.querySelectorAll(".event__match.event__match--static.event__match--twoLine"))
      .map(element => element?.id?.replace("g_1_", ""));
  });

  await page.close();
  return matchIdList;
}

export const getMatchData = async (browser, matchId) => {
  const page = await browser.newPage();

  const url = `${BASE_URL}/match/${matchId}/#/match-summary/match-statistics/0`;
  await page.goto(url);

  await new Promise(resolve => setTimeout(resolve, 1500));

  const data = await page.evaluate(async _ => ({
    date: document.querySelector(".duelParticipant__startTime")?.outerText,
    home: {
      name: document.querySelector(".duelParticipant__home .participant__participantName.participant__overflow")?.outerText,
      image: document.querySelector(".duelParticipant__home .participant__image")?.src
    },
    away: {
      name: document.querySelector(".duelParticipant__away .participant__participantName.participant__overflow")?.outerText,
      image: document.querySelector(".duelParticipant__away .participant__image")?.src
    },
    result: {
      home: Array.from(document.querySelectorAll(".detailScore__wrapper span:not(.detailScore__divider)"))?.[0]?.outerText,
      away: Array.from(document.querySelectorAll(".detailScore__wrapper span:not(.detailScore__divider)"))?.[1]?.outerText,
      penalty: document.querySelector(".detailScore__fullTime")?.textContent,
      status: document.querySelector(".fixedHeaderDuel__detailStatus")?.outerText
    },
    statistics: Array.from(document.querySelectorAll(".section > ._row_n1rcj_9 > ._category_n1rcj_16"))
      .map(element => ({
        categoryName: element.querySelector("._category_1vze3_5")?.outerText,
        homeValue: element.querySelector("._homeValue_bwnrp_10")?.outerText,
        awayValue: element.querySelector("._awayValue_bwnrp_14")?.outerText,
      }))
  }));

  await page.close();
  return data;
}

export const writeMatchData = (data, pathW, name) => {
  const jsonData = JSON.stringify(data, null, 2);
  const filePath = path.join(pathW, `${name}.json`);

  fs.mkdir(path.dirname(filePath), { recursive: true }, (err) => {
    if (err) {
      console.error("Error creating directories:", err);
    } else {
      fs.writeFile(filePath, jsonData, (err) => {
        if (err) {
          console.error("Error writing to JSON file:", err);
        }
      });
    }
  });
}
