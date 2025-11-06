// JavaScript Document

// TODO: This really should be a class with an instance variable
//       parked in the outermost frame and used by all loaded pages.
//       Create instance via JS include file.

//
// Course Configuration
//


var titleProgram = ''
var titleCourse = 'CRAFT: Help with PTSD for you and your family'

var docDisclaimer = "This document will open in a new window or tab. Once you have completed your use of this document, close the window or tab that contains it. The course is still open and you will be taken back to your location in the course.";


function showDisclaimer()
{
   alert(''+docDisclaimer);
}

//
// Format for the menu/lesson directory array is as follows...
//
// The idea is that each menu level has the following:
//
//  - A list of selectable entries
//
//  - An internal menu name (used mostly for debugging)
//
//  - A string that means something to the user.  This is the title of
//    the group.  For a course this is the course title.  For a lesson
//    that has subsections this would be the section name.  If (for a
//    submenu) this is null or empty then the menu entry name of the
//    parent entry should be used.
//
// Generally, the idea is that if a group is selectable then it will have
// a name an a URL.  If not, then there will be no name for the entry, no
// URL and the group name of the submenu will be used in any tree structured
// presentation and will not be clickable.
//
// There is one entry for every menu entry and these must appear in the order
// that the entries are to be presented.  The array entries themselves are arrays
// that contain:
//
//  - The number of pages in the section, including a total of any subsection page counts
//  - Does this session have an assessment?
//  - End of lesson quiz or assessment page
//  - The text of the menu entry
//  - A URL reference for the page to be transitioned to.
//
// The context that this info is drawn in is created by drawSideMenu().
// The array is used by the buildMenu routine that is part of a 'menuOnLoad()'
// function (currently located in global.js) that uses is to build a <ul>
// HTML segment that is appended to the node(s) created by drawSideMenu()
// using a jQuery append.
//

function setAT()
{
    alert(window.location);
}

var lesson = new Array();
// Usage of indexes for mMenu data entries in the array
var MENU_PAGECNT_IDX = 0;
var MENU_PAGEARRAY_IDX = 1;
var MENU_ASSESSMENT_IDX = 2;
var MENU_ASSESSMENTURL_IDX = 3;
var MENU_TITLE_IDX = 4;
var MENU_URL_IDX = 5;
var MENU_GROUP_IDX = 6;


// Handle some of the details of attaching a submenu to a menu.
// We total the submenu pages and add them to the menu entry.
// This allows all menu entries to be defined identically.
function fixupSubmenu (pLsm, pName) {
    pLsm.menuName = pName;
    lesson[lesson.length-1].subMenu = pLsm;
    var lsmCount = 0;
    for (var i = 0; i < pLsm.length; i++) {
        lsmCount += pLsm[i].menuEntryData[MENU_PAGECNT_IDX];
        // for(var j = 0; j < pLsm[i].menuEntryData[MENU_PAGEARRAY_IDX].length; j++){
        //     lesson[lesson.length-1].menuEntryData[MENU_PAGEARRAY_IDX].push(pLsm[i].menuEntryData[MENU_PAGEARRAY_IDX][j]);
        // };
    }
    //console.log('new array :: ', lesson[lesson.length-1].menuEntryData[MENU_PAGEARRAY_IDX]);
    lesson[lesson.length-1].menuEntryData[MENU_PAGECNT_IDX] += lsmCount;
}

// Welcome
lesson.push({ menuEntryData: [ 1, ["001"],"none","#","Welcome","lesson00/00_001.htm", null ] });

// Section 1
// lesson.push({ menuEntryData: [ 16,"none","#","Section 1: Introduction (Lesson 1)","lesson01/01_001.htm" ] });
lesson.push({ menuEntryData: [ 16, ["001","002","003","005","006","007","008","009","010","011","012","013","014","015","016","017"],"none","#","Section 1: Introduction (Lesson 1)","lesson01/01_001.htm", "01" ] });

// Section 2
lesson.push({ menuEntryData: [ 13, ["001","002","003","004","005","006","007","008","009","010","011","012","013"],"none","#","Section 2: Safety Planning (Lesson 2)","lesson02/02_001.htm", "02" ] });

// Section 3
lesson.push({ menuEntryData: [ 1, ["001"],"none","#","Section 3: Improve the Situation: ","lesson03/03_001.htm", null ] });
//lsm = new Array();
lesson.push({ menuEntryData: [ 24, ["001","002","003","004","005","006","007","008","009","010","011","012","013","014","015","016","017","018","019","020","021","022","023","024"],"none","#","Section 3: Understand PTSD (Lesson 3)","lesson04/04_001.htm", "04" ] });
lesson.push({ menuEntryData: [ 14, ["001","002","003","004","005","006","007","008","009","010","011","012","013","014"],"none","#","Section 3: Increase Positive Behaviors (Lesson 4)","lesson05/05_001.htm", "05" ] });
//fixupSubmenu(lsm, "improve");

// Section 4
lesson.push({ menuEntryData: [ 1, ["001"],"none","#","Section 4: Care for Yourself","lesson06/06_001.htm", null ] });
//lsm = new Array();
lesson.push({ menuEntryData: [ 15,["001","002","003","004","005","006","007","008","009","010","011","012","013","014","015"],"none","#","Section 4: Use Self-Rewards and Social Support (Lesson 5)","lesson07/07_001.htm", "07" ] });
lesson.push({ menuEntryData: [ 13,["001","002","003","004","005","006","007","008","009","010","011","012","013"],"none","#","Section 4: Improve Problem Solving (Lesson 6)","lesson08/08_001.htm", "08" ] });
lesson.push({ menuEntryData: [ 17,["001","002","003","004","005","006","007","008","009","010","011","012","013","014","015","016","017"],"none","#","Section 4: Reduce Stress and Improve Sleep (Lesson 7)","lesson09/09_001.htm", "09" ] });
//fixupSubmenu(lsm, "yourself");

// Section 5
lesson.push({ menuEntryData: [ 1,["001"],"none","#","Section 5: Rebuild Your Relationship","lesson10/10_001.htm", null ] });
//lsm = new Array();
lesson.push({ menuEntryData: [ 13,["001","002","003","004","005","006","007","008","009","010","011","012","013"],"none","#","Section 5: Practice Positive Communication (Lesson 8)","lesson11/11_001.htm", "11" ] });
lesson.push({ menuEntryData: [ 13,["001","002","003","004","005","006","007","008","009","010","011","012","013"],"none","#","Section 5: Share Pleasant Activities (Lesson 9)","lesson12/12_001.htm", "12" ] });
//fixupSubmenu(lsm, "rebuild");

// Section 6
lesson.push({ menuEntryData: [ 1,["001"],"none","#","Section 6: Get Your Veteran into Care ","lesson13/13_001.htm", null ] });
//lsm = new Array();
lesson.push({ menuEntryData: [ 13,["001","002","003","004","005","006","007","008","009","010","011","012","013"],"none","#","Section 6: Explore Treatment Options (Lesson 10)","lesson14/14_001.htm", "14" ] });
lesson.push({ menuEntryData: [ 15,["001","002","003","004","005","006","007","008","009","010","011","012","013","014","015"],"none","#","Section 6: Discuss Treatment Options with Your Veteran (Lesson 11)","lesson15/15_001.htm", "15" ] });
lesson.push({ menuEntryData: [ 20,["001","002","003","004","005","006","007","008","009","010","011","012","013","014","015","016","017","018","019","020"],"none","#","Section 6: Supporting Your Loved One's Treatment (Lesson 12)","lesson16/16_001.htm", "16" ] });
//fixupSubmenu( lsm, "treatment" );


lesson.groupName = titleCourse; // People pleas'n name
lesson.menuName = 'main';   // Internal name for menu

// end config.js


// JIRA
/*setTimeout(function() {
    var script = document.createElement('script');
    script.setAttribute('src', 'https://alleninteractions.atlassian.net/s/75b8b7b27df0b88219220daf07ae6e51-T/en_USerdr6m/71001/bcac6fa509afb45dbe7807978999e5ac/2.0.9/_/download/batch/com.atlassian.jira.collector.plugin.jira-issue-collector-plugin:issuecollector/com.atlassian.jira.collector.plugin.jira-issue-collector-plugin:issuecollector.js?locale=en-US&collectorId=28e3342c');

    var wrapper = document.getElementsByTagName('body')[0];
    wrapper.appendChild(script);
}, 200);*/