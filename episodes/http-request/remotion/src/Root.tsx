import React from 'react';
import {Composition, Still} from 'remotion';
import {
  BrowserCertificateGallery, BrowserChromeGallery, BrowserPair, BrowserTypingGallery,
  CafeSceneGallery, CafeSceneScrambledGallery, Network404Gallery, NetworkDoneGallery,
  NetworkPendingGallery, NetworkWaterfallGallery, PhoneContactsGallery,
  StyledPageGallery, StyledPageRevealGallery,
  WireframePageGallery, FileManagerGallery, FileCardGallery, FlyingLabelGallery,
  StepBarGallery, KeyCapGallery, ImagePlaceholderGallery,
} from './Gallery';
import {VIDEO} from './theme';
import {Main, MAIN_VIDEO} from './Main';
import {COVER_SIZES, Cover16x9, Cover4x3, Cover3x4} from './Cover';

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Main" component={Main} {...MAIN_VIDEO} />
    <Composition id="Cover16x9" component={Cover16x9} width={COVER_SIZES['16x9'].width} height={COVER_SIZES['16x9'].height} fps={MAIN_VIDEO.fps} durationInFrames={1} />
    <Composition id="Cover4x3" component={Cover4x3} width={COVER_SIZES['4x3'].width} height={COVER_SIZES['4x3'].height} fps={MAIN_VIDEO.fps} durationInFrames={1} />
    <Composition id="Cover3x4" component={Cover3x4} width={COVER_SIZES['3x4'].width} height={COVER_SIZES['3x4'].height} fps={MAIN_VIDEO.fps} durationInFrames={1} />
    <Still id="WireframePage" component={WireframePageGallery} width={VIDEO.width} height={VIDEO.height} />
    <Still id="FileManager" component={FileManagerGallery} width={VIDEO.width} height={VIDEO.height} />
    <Still id="FileCard" component={FileCardGallery} width={VIDEO.width} height={VIDEO.height} />
    <Still id="FlyingLabel" component={FlyingLabelGallery} width={VIDEO.width} height={VIDEO.height} />
    <Still id="StepBar" component={StepBarGallery} width={VIDEO.width} height={VIDEO.height} />
    <Still id="KeyCap" component={KeyCapGallery} width={VIDEO.width} height={VIDEO.height} />
    <Still id="ImagePlaceholder" component={ImagePlaceholderGallery} width={VIDEO.width} height={VIDEO.height} />
    <Still id="BrowserChrome" component={BrowserChromeGallery} width={VIDEO.width} height={VIDEO.height} />
    <Still id="BrowserPair" component={BrowserPair} width={VIDEO.width} height={VIDEO.height} />
    <Still id="StyledPage" component={StyledPageGallery} width={VIDEO.width} height={VIDEO.height} />
    <Still id="BrowserTyping" component={BrowserTypingGallery} width={VIDEO.width} height={VIDEO.height} />
    <Still id="BrowserCertificate" component={BrowserCertificateGallery} width={VIDEO.width} height={VIDEO.height} />
    <Still id="StyledPageReveal" component={StyledPageRevealGallery} width={VIDEO.width} height={VIDEO.height} />
    <Still id="NetworkPending" component={NetworkPendingGallery} width={VIDEO.width} height={VIDEO.height} />
    <Still id="NetworkDone" component={NetworkDoneGallery} width={VIDEO.width} height={VIDEO.height} />
    <Still id="Network404" component={Network404Gallery} width={VIDEO.width} height={VIDEO.height} />
    <Still id="NetworkWaterfall" component={NetworkWaterfallGallery} width={VIDEO.width} height={VIDEO.height} />
    <Still id="PhoneContacts" component={PhoneContactsGallery} width={VIDEO.width} height={VIDEO.height} />
    <Still id="CafeScene" component={CafeSceneGallery} width={VIDEO.width} height={VIDEO.height} />
    <Still id="CafeSceneScrambled" component={CafeSceneScrambledGallery} width={VIDEO.width} height={VIDEO.height} />
  </>
);
