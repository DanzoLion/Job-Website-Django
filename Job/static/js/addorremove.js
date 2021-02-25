function addorremove(id) {
            if (id){
                var wishlist = $('#jobwl'+id).data('wl'); // id is used in the above function we are referencing
                if(wishlist == 0) {
                    $.ajax({
                        url: "users/add-wishlist/" + id,
                        method: "GET",
                        success: function () {
                            $('#jobwl' + id).removeClass('btn-primary').addClass('btn-danger')
                            const Toast = Swal.mixin({
                                toast: true,
                                position: 'top',
                                showConfirmButton: true,
                                timer: 2000,
                                timerProgressBar: true,
                                onOpen: (toast) => {
                                    toast.addEventListener('mouseenter', Swal.stopTimer)
                                    toast.addEventListener('mouseleave', Swal.resumeTimer)
                                }
                            })

                            Toast.fire({
                                icon: 'success',
                                title: 'Thanks! Added!'
                            })
                            $('#jobwl'+id).data('wl', 1); // where 1 means we have added an element in our wishlist and it == True
                        }
                    });
                }else{

                    $.ajax({
                    url:"users/remove-from-wishlist/" + id,
                    method: "GET",
                    success: function() {
                        $('#jobwl'+id).removeClass('btn-danger').addClass('btn-primary')
                        const Toast = Swal.mixin({
                                  toast: true,
                                  position: 'top-end',
                                  showConfirmButton: true,
                                  timer: 3000,
                                  timerProgressBar: true,
                                  onOpen: (toast) => {
                                    toast.addEventListener('mouseenter', Swal.stopTimer)
                                    toast.addEventListener('mouseleave', Swal.resumeTimer)
                                  }
                                })

                                Toast.fire({
                                  icon: 'success',
                                  title: 'Aw Removed!'
                                })
                        $('#jobwl'+id).data('wl', 0); // where 0 means we have removed an element in our wishlist and it == False
                        }
                    });

                    }
                }
            }

