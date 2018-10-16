# The MIT License (MIT)
# Copyright (c) 2018 by EUMETSAT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import tornado.escape

from ..webservice import WsRequestHandler
from ..reqparams import RequestParams
from ..controllers.datasets import *
from ..controllers.docfiles import *
from ..controllers.service import *
from ..controllers.store import *
from ..controllers.users import *
from ..models.bucket import Bucket
from ..models.dataset import Dataset
from ..models.dataset_query import DatasetQuery
from ..models.dataset_query_result import DatasetQueryResult
from ..models.dataset_ref import DatasetRef
from ..models.dataset_validation_result import DatasetValidationResult
from ..models.doc_file_ref import DocFileRef
from ..models.issue import Issue
from ..models.user import User


# noinspection PyAbstractClass,PyShadowingBuiltins
class ServiceInfo(WsRequestHandler):

    def get(self):
        """Provide API operation getServiceInfo()."""
        result = get_service_info(self.ws_context)

        # transform result of type Dict into response with mime-type application/json
        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(result))


# noinspection PyAbstractClass,PyShadowingBuiltins
class StoreInfo(WsRequestHandler):

    def get(self):
        """Provide API operation getStoreInfo()."""
        result = get_store_info(self.ws_context)

        # transform result of type Dict into response with mime-type application/json
        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(result))


# noinspection PyAbstractClass,PyShadowingBuiltins
class StoreUpload(WsRequestHandler):

    def post(self):
        """Provide API operation uploadStoreFiles()."""
        # transform body with mime-type multipart/form-data into a Dict
        # TODO (generated): transform self.request.body first
        data = self.request.body

        result = upload_store_files(self.ws_context, data=data)
        self.finish()


# noinspection PyAbstractClass,PyShadowingBuiltins
class StoreDownload(WsRequestHandler):

    def get(self):
        """Provide API operation downloadStoreFiles()."""
        expr = self.query.get_param('expr', default=None)
        region = self.query.get_param_float_list('region', default=None)
        time = self.query.get_param_list('time', default=None)
        wdepth = self.query.get_param_float_list('wdepth', default=None)
        mtype = self.query.get_param('mtype', default='all')
        wlmode = self.query.get_param('wlmode', default='all')
        shallow = self.query.get_param('shallow', default='no')
        pmode = self.query.get_param('pmode', default='contains')
        pgroup = self.query.get_param_list('pgroup', default=None)
        pname = self.query.get_param_list('pname', default=None)
        docs = self.query.get_param_bool('docs', default=False)
        result = download_store_files(self.ws_context, expr=expr, region=region, time=time, wdepth=wdepth, mtype=mtype, wlmode=wlmode, shallow=shallow, pmode=pmode, pgroup=pgroup, pname=pname, docs=docs)

        # transform result of type str into response with mime-type application/octet-stream
        # TODO (generated): transform result first
        self.finish(result)


# noinspection PyAbstractClass,PyShadowingBuiltins
class DatasetsValidate(WsRequestHandler):

    def post(self):
        """Provide API operation validateDataset()."""
        # transform body with mime-type application/json into a Dataset
        data_dict = tornado.escape.json_decode(self.request.body)
        data = Dataset.from_dict(data_dict)

        result = validate_dataset(self.ws_context, data=data)

        # transform result of type DatasetValidationResult into response with mime-type application/json
        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(result.to_dict()))


# noinspection PyAbstractClass,PyShadowingBuiltins
class Datasets(WsRequestHandler):

    def get(self):
        """Provide API operation findDatasets()."""
        expr = self.query.get_param('expr', default=None)
        region = self.query.get_param_float_list('region', default=None)
        time = self.query.get_param_list('time', default=None)
        wdepth = self.query.get_param_float_list('wdepth', default=None)
        mtype = self.query.get_param('mtype', default='all')
        wlmode = self.query.get_param('wlmode', default='all')
        shallow = self.query.get_param('shallow', default='no')
        pmode = self.query.get_param('pmode', default='contains')
        pgroup = self.query.get_param_list('pgroup', default=None)
        pname = self.query.get_param_list('pname', default=None)
        offset = self.query.get_param_int('offset', default=1)
        count = self.query.get_param_int('count', default=1000)
        result = find_datasets(self.ws_context, expr=expr, region=region, time=time, wdepth=wdepth, mtype=mtype, wlmode=wlmode, shallow=shallow, pmode=pmode, pgroup=pgroup, pname=pname, offset=offset, count=count)

        # transform result of type DatasetQueryResult into response with mime-type application/json
        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(result.to_dict()))

    def put(self):
        """Provide API operation addDataset()."""
        # transform body with mime-type application/json into a Dataset
        data_dict = tornado.escape.json_decode(self.request.body)
        data = Dataset.from_dict(data_dict)

        result = add_dataset(self.ws_context, data=data)

        # transform result of type DatasetRef into response with mime-type application/json
        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(result.to_dict()))

    def post(self):
        """Provide API operation updateDataset()."""
        # transform body with mime-type application/json into a Dataset
        data_dict = tornado.escape.json_decode(self.request.body)
        data = Dataset.from_dict(data_dict)

        result = update_dataset(self.ws_context, data=data)
        self.finish()


# noinspection PyAbstractClass,PyShadowingBuiltins
class DatasetsId(WsRequestHandler):

    def get(self, id: str):
        """Provide API operation getDatasetById()."""
        id_ = id
        result = get_dataset_by_id(self.ws_context, id_=id_)

        # transform result of type Dataset into response with mime-type application/json
        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(result.to_dict()))

    def delete(self, id: str):
        """Provide API operation deleteDataset()."""
        api_key = self.header.get_param('api_key', default=UNDEFINED)
        id_ = id
        result = delete_dataset(self.ws_context, api_key=api_key, id_=id_)
        self.finish()


# noinspection PyAbstractClass,PyShadowingBuiltins
class DatasetsAffilProjectCruise(WsRequestHandler):

    def get(self, affil: str, project: str, cruise: str):
        """Provide API operation getDatasetsInBucket()."""
        result = get_datasets_in_bucket(self.ws_context, affil=affil, project=project, cruise=cruise)

        # transform result of type List[DatasetRef] into response with mime-type application/json
        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(result.to_dict()))


# noinspection PyAbstractClass,PyShadowingBuiltins
class DatasetsAffilProjectCruiseName(WsRequestHandler):

    def get(self, affil: str, project: str, cruise: str, name: str):
        """Provide API operation getDatasetByBucketAndName()."""
        result = get_dataset_by_bucket_and_name(self.ws_context, affil=affil, project=project, cruise=cruise, name=name)

        # transform result of type str into response with mime-type application/octet-stream
        # TODO (generated): transform result first
        self.finish(result)


# noinspection PyAbstractClass,PyShadowingBuiltins
class Docfiles(WsRequestHandler):

    def put(self):
        """Provide API operation addDocFile()."""
        # transform body with mime-type multipart/form-data into a Dict
        # TODO (generated): transform self.request.body first
        data = self.request.body

        result = add_doc_file(self.ws_context, data=data)
        self.finish()

    def post(self):
        """Provide API operation updateDocFile()."""
        # transform body with mime-type multipart/form-data into a Dict
        # TODO (generated): transform self.request.body first
        data = self.request.body

        result = update_doc_file(self.ws_context, data=data)
        self.finish()


# noinspection PyAbstractClass,PyShadowingBuiltins
class DocfilesAffilProjectCruise(WsRequestHandler):

    def get(self, affil: str, project: str, cruise: str):
        """Provide API operation getDocFilesInBucket()."""
        result = get_doc_files_in_bucket(self.ws_context, affil=affil, project=project, cruise=cruise)

        # transform result of type List[DocFileRef] into response with mime-type application/json
        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(result.to_dict()))


# noinspection PyAbstractClass,PyShadowingBuiltins
class DocfilesAffilProjectCruiseName(WsRequestHandler):

    def get(self, affil: str, project: str, cruise: str, name: str):
        """Provide API operation downloadDocFile()."""
        result = download_doc_file(self.ws_context, affil=affil, project=project, cruise=cruise, name=name)

        # transform result of type str into response with mime-type application/octet-stream
        # TODO (generated): transform result first
        self.finish(result)

    def delete(self, affil: str, project: str, cruise: str, name: str):
        """Provide API operation deleteDocFile()."""
        result = delete_doc_file(self.ws_context, affil=affil, project=project, cruise=cruise, name=name)
        self.finish()


# noinspection PyAbstractClass,PyShadowingBuiltins
class Users(WsRequestHandler):

    def post(self):
        """Provide API operation createUser()."""
        # transform body with mime-type application/json into a User
        data_dict = tornado.escape.json_decode(self.request.body)
        data = User.from_dict(data_dict)

        result = create_user(self.ws_context, data=data)
        self.finish()


# noinspection PyAbstractClass,PyShadowingBuiltins
class UsersLogin(WsRequestHandler):

    def get(self):
        """Provide API operation loginUser()."""
        username = self.query.get_param('username', default=UNDEFINED)
        password = self.query.get_param('password', default=UNDEFINED)
        result = login_user(self.ws_context, username=username, password=password)

        # transform result of type str into response with mime-type application/json
        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(result))


# noinspection PyAbstractClass,PyShadowingBuiltins
class UsersLogout(WsRequestHandler):

    def get(self):
        """Provide API operation logoutUser()."""
        result = logout_user(self.ws_context)
        self.finish()


# noinspection PyAbstractClass,PyShadowingBuiltins
class UsersId(WsRequestHandler):

    def get(self, id: str):
        """Provide API operation getUserByID()."""
        id_ = RequestParams.to_int('id', id)
        result = get_user_by_id(self.ws_context, id_=id_)

        # transform result of type User into response with mime-type application/json
        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(result.to_dict()))

    def put(self, id: str):
        """Provide API operation updateUser()."""
        id_ = RequestParams.to_int('id', id)
        # transform body with mime-type application/json into a User
        data_dict = tornado.escape.json_decode(self.request.body)
        data = User.from_dict(data_dict)

        result = update_user(self.ws_context, id_=id_, data=data)
        self.finish()

    def delete(self, id: str):
        """Provide API operation deleteUser()."""
        id_ = RequestParams.to_int('id', id)
        result = delete_user(self.ws_context, id_=id_)
        self.finish()
