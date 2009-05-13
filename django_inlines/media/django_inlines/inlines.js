var DjangoInlines = DjangoInlines || {}


$(function() {
  
  $('.vInlineTextArea').each(function(){
    var id = this.id;
    var div = $('<div id="inline_control_for_'+id+'" class="inline_control"><p class="insert">Insert inline: </p></div>');
    var select = $('<select><option value="">----</option></select>');
    for (inline in DjangoInlines.inlines) { select.append($('<option value='+DjangoInlines.inlines[inline]+'>'+DjangoInlines.inlines[inline]+'</option>'))};
    div.append($('<div class="inlineinserter" id="'+id+'_inlineinserter"></div>'))
    
    select.change(function(){
      var inline = $(this).val();
      var inserter = $('#'+id+'_inlineinserter');
      if (inline == '') { inserter.html(''); return false }
      inserter.load(DjangoInlines.get_inline_form_url + "?inline="+$(this).val()+"&target="+id);
    });
    
    div.find('p').append(select);
    $(this).after(div);
  });

  
  $("div.inlineinserter .insert").live("click", function(){
    target = $(this).attr('rel');
    parent = $(this).parents('div.inline_control');
    var inline_text = ""
    inline_text += parent.find('p.insert select').val();
    variant = $('#'+target+'_variant').val();
    if (variant) {
      inline_text += ':'+variant
    }
    inline_text += ' '
    inline_text += $('#id_'+target+'_value').val();
    parent.find('p.arg .value').each(function() {
      if ($(this).val() != '') {
        inline_text += ' '+$(this).attr('rel')+'='+$(this).val();
      }
    });
    $('#'+target).replaceSelection("{{ "+inline_text+" }} ");
  });

  $("div.inlineinserter a.cancel").live("click", function(){
    $(this).parents('div.inline_control').find('p.insert select').val(['']).change();
    return false;
  });
  
});