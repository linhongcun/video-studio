import {Still} from 'remotion';
import {Cover} from './Cover';
const empty = {spec: null as any, assets: {}};
export const Root = () => (
  <>
    <Still id="Cover169" component={Cover as any} width={1920} height={1080} defaultProps={{...empty, size: '16x9'}} />
    <Still id="Cover43" component={Cover as any} width={1440} height={1080} defaultProps={{...empty, size: '16x9', offsetX: 240}} />
    <Still id="Cover34" component={Cover as any} width={1080} height={1440} defaultProps={{...empty, size: '3x4'}} />
  </>
);
